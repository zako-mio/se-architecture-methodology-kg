#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_publish.py — 公开仓装配唯一入口（声明式分区 + 预检 + 对账）。

规则唯一来源：同目录 `publish-manifest.json`（见 PUBLISH-PIPELINE-CONTRACT.md §3）。
本脚本是唯一允许写 `_publish/` 的入口；产物不含任何时间戳/随机量，保证幂等。

CLI（契约 §4）：
  --check                     对账（只读），有差异 exit 1
  --apply                     装配（先预检 P1–P5，后落盘）
  --apply --dry-run           只打印计划 + 预检结果，不写盘
  --check-public              纯 target 侧校验（CI 模式，不依赖 MROOT/staging）
  --export DIR                导出 Pages 白名单到 DIR
  --assert-clean DIR          断言 DIR 无私有路径命中、无 binary_exts 文件
  --refresh-sanitize          先跑 audit_publish.py --emit 再继续

附加（非契约，便于对账集成）：
  --json                      --check 时额外输出机读 JSON
  --root DIR                  --check-public/--export/--assert-clean 的源根（默认 .）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MROOT = os.path.dirname(SCRIPT_DIR)
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "publish-manifest.json")

CLASSES = ("private", "never", "preserve", "sanitize", "mirror", "mask")

# 复用 audit_publish 的脱敏正则，保证「mask 类」与 audit 链同源同规则
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
import audit_publish as _ap  # noqa: E402


def mask_text(text):
    """与 audit_publish.mask_sensitive 同规则的本机路径脱敏（顺序：先 Windows 后 home）。"""
    text = _ap.WIN_PATH_RE.sub("%USERPROFILE%", text)
    return _ap.HOME_PATH_RE.sub("~", text)


# ---------------------------------------------------------------------------
# 路径与哈希工具
# ---------------------------------------------------------------------------
def norm(p):
    """统一为 posix 相对路径，去 './' 与尾部 '/'。"""
    p = str(p).replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p


def basename(p):
    return norm(p).rsplit("/", 1)[-1]


def is_under(rel, base):
    """rel 等于 base 或位于 base 之下（posix 语义）。"""
    rel = norm(rel)
    base = norm(base)
    if rel == base:
        return True
    return rel.startswith(base + "/")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path=MANIFEST_PATH):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ---------------------------------------------------------------------------
# manifest 解析
# ---------------------------------------------------------------------------
def class_items(manifest, cls):
    """返回 [(path, excludes)]；支持字符串与 {path, exclude} 两种写法。"""
    out = []
    for item in manifest["classes"].get(cls, []):
        if isinstance(item, str):
            out.append((norm(item), []))
        elif isinstance(item, dict):
            p = norm(item["path"])
            ex = item.get("exclude", [])
            if isinstance(ex, str):
                ex = [ex]
            out.append((p, [norm(x) for x in ex]))
        else:
            raise ValueError("manifest class %s 含非法条目: %r" % (cls, item))
    return out


def matches_exclude(rel_within, excludes):
    """exclude 为 basename 或相对子路径（相对镜像基）。"""
    for ex in excludes:
        if "/" in ex:
            if rel_within == ex or rel_within.startswith(ex + "/"):
                return True
        elif basename(rel_within) == ex:
            return True
    return False


def matches_any_path(rel, bases):
    return any(is_under(rel, b) for b in bases)


def is_preserve(rel, manifest):
    return matches_any_path(rel, [norm(p) for p in manifest["classes"]["preserve"]])


def is_never(rel, manifest):
    """never 命中：带 '/' 的按前缀；纯名字（如 __pycache__、.git）按路径分量匹配。"""
    rel = norm(rel)
    comps = set(rel.split("/"))
    for p in manifest["classes"]["never"]:
        pn = norm(p)
        if "/" in pn:
            if is_under(rel, pn):
                return True
        elif pn in comps or is_under(rel, pn):
            return True
    return False


def is_binary(rel, manifest):
    exts = {e.lower() for e in manifest["binary_exts"]}
    return os.path.splitext(rel)[1].lower() in exts


def binary_allowlist(manifest):
    return [norm(p) for p in manifest.get("binary_allowlist", [])]


def binary_allowed(rel, manifest):
    """显式声明的合法二进制（如站点引用的 png 示意图）；未声明即为违规（fail-closed）。"""
    return matches_any_path(rel, binary_allowlist(manifest))


def binary_violations(rels, manifest):
    return [r for r in sorted(rels) if is_binary(r, manifest) and not binary_allowed(r, manifest)]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_bytes(entry):
    """按类返回「目标侧应有的字节」：mask 类对文本做路径脱敏，其余原样。"""
    with open(entry["src_abs"], "rb") as fh:
        raw = fh.read()
    if entry.get("class") != "mask":
        return raw
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw          # 二进制不脱敏
    return mask_text(text).encode("utf-8")


def probe_hit(rel, manifest):
    """命中 private_probe 则返回命中的 probe，否则 None。"""
    for p in manifest["private_probe"]:
        pn = norm(p)
        if "/" in pn:
            if is_under(rel, pn):
                return pn
        elif basename(rel) == pn:
            return pn
    return None


# ---------------------------------------------------------------------------
# 期望集合
# ---------------------------------------------------------------------------
def iter_tree(base_abs):
    """产出 (abs_path, rel_to_base)（仅文件，已排序）。"""
    if os.path.isfile(base_abs):
        yield base_abs, basename(base_abs)
        return
    for root, dirs, files in os.walk(base_abs):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            yield p, norm(os.path.relpath(p, base_abs))


def build_expected(manifest):
    """返回 (expected, sanitize_missing, mirror_missing)。

    expected: rel -> {class, src_abs, src_rel}
    """
    staging_dir = norm(manifest["staging_dir"])
    staging_abs = os.path.join(MROOT, staging_dir)
    expected = {}
    sanitize_missing = []
    mirror_missing = []

    for base, excludes in class_items(manifest, "mirror"):
        src_abs = os.path.join(MROOT, base)
        if not os.path.exists(src_abs):
            mirror_missing.append(base)
            continue
        for abs_p, within in iter_tree(src_abs):
            rel = norm(os.path.relpath(abs_p, MROOT))
            if matches_exclude(within, excludes):
                continue
            if is_never(rel, manifest):
                continue
            expected[rel] = {"class": "mirror", "src_abs": abs_p, "src_rel": rel}

    for base, excludes in class_items(manifest, "mask"):
        src_abs = os.path.join(MROOT, base)
        if not os.path.exists(src_abs):
            mirror_missing.append(base)
            continue
        for abs_p, within in iter_tree(src_abs):
            rel = norm(os.path.relpath(abs_p, MROOT))
            if matches_exclude(within, excludes):
                continue
            if is_never(rel, manifest):
                continue
            expected[rel] = {"class": "mask", "src_abs": abs_p, "src_rel": rel}

    for base, excludes in class_items(manifest, "sanitize"):
        src_abs = os.path.join(staging_abs, base)
        if not os.path.exists(src_abs):
            sanitize_missing.append(base)
            continue
        for abs_p, within in iter_tree(src_abs):
            rel = norm(os.path.relpath(abs_p, staging_abs))
            if matches_exclude(within, excludes):
                continue
            if is_never(rel, manifest):
                continue
            expected[rel] = {
                "class": "sanitize",
                "src_abs": abs_p,
                "src_rel": norm(os.path.join(staging_dir, rel)),
            }
    return expected, sanitize_missing, mirror_missing


# ---------------------------------------------------------------------------
# target 扫描与差异
# ---------------------------------------------------------------------------
def scan_actual(root_abs):
    actual = {}
    if not os.path.isdir(root_abs):
        return actual
    for root, dirs, files in os.walk(root_abs):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = norm(os.path.relpath(p, root_abs))
            actual[rel] = p
    return actual


def target_path(manifest):
    return os.path.join(MROOT, norm(manifest["target_dir"]))


def compute_diff(manifest, expected, target_abs):
    actual = scan_actual(target_abs)
    missing = sorted(r for r in expected if r not in actual)
    extra = sorted(
        r
        for r in actual
        if r not in expected
        and not is_preserve(r, manifest)
        and not is_never(r, manifest)
    )
    modified = []
    for r in sorted(expected):
        if r in actual and sha256_bytes(content_bytes(expected[r])) != sha256_of(actual[r]):
            modified.append(r)
    return missing, extra, modified


# ---------------------------------------------------------------------------
# 预检闸 P1–P5
# ---------------------------------------------------------------------------
def default_deny_errors(manifest):
    """P1：MROOT 顶层每个条目恰好被一个类（顶层声明）覆盖。"""
    top = sorted(os.listdir(MROOT))
    decl = {}
    for cls in CLASSES:
        for p, _ in class_items(manifest, cls):
            if "/" not in p:  # 仅顶层声明参与顶层覆盖判定
                decl.setdefault(p, set()).add(cls)
    errors = []
    for e in top:
        if e not in decl:
            errors.append("未声明: %s" % e)
    for name in sorted(decl):
        cs = decl[name]
        if len(cs) > 1:
            errors.append("重复声明: %s -> %s" % (name, sorted(cs)))
    return errors, decl


def preflight(manifest, expected, sanitize_missing):
    res = {}
    errs, decl = default_deny_errors(manifest)
    res["P1"] = {"name": "默认拒绝覆盖检查", "ok": not errs, "detail": errs}

    p2 = [r for r in sorted(expected) if probe_hit(r, manifest)]
    res["P2"] = {"name": "期望集合 private_probe 命中==0", "ok": not p2, "detail": p2}

    p3 = binary_violations(expected, manifest)
    al = binary_allowlist(manifest)
    res["P3"] = {"name": "期望集合二进制仅含 binary_allowlist（allowlist=%d 项）" % len(al),
                 "ok": not p3, "detail": p3}

    p4 = sorted(set(sanitize_missing))
    res["P4"] = {"name": "sanitize 类 staging 文件齐备", "ok": not p4, "detail": p4}

    p5 = [r for r in sorted(expected) if is_preserve(r, manifest)]
    res["P5"] = {"name": "preserve 不进入期望集合", "ok": not p5, "detail": p5}
    return res


def print_preflight(pf):
    print("--- 预检闸 P1–P5 ---")
    for k in ("P1", "P2", "P3", "P4", "P5"):
        g = pf[k]
        print("[%s] %-4s %s (%d)" % (k, "OK" if g["ok"] else "FAIL", g["name"], len(g["detail"])))
        for d in g["detail"]:
            print("      - %s" % d)


# ---------------------------------------------------------------------------
# 落盘
# ---------------------------------------------------------------------------
def prune_empty_dirs(target_abs, manifest):
    for root, dirs, files in os.walk(target_abs, topdown=False):
        if os.path.abspath(root) == os.path.abspath(target_abs):
            continue
        rel = norm(os.path.relpath(root, target_abs))
        if is_preserve(rel, manifest) or is_never(rel, manifest):
            continue
        try:
            if not os.listdir(root):
                os.rmdir(root)
        except OSError:
            pass


def write_state(manifest, expected, target_abs):
    files = {}
    p2 = p3 = 0
    for rel in sorted(expected):
        src = expected[rel]["src_abs"]
        dst = os.path.join(target_abs, rel)
        files[rel] = {
            "sha256": sha256_of(dst),
            "class": expected[rel]["class"],
            "src": expected[rel]["src_rel"],
            "src_sha256": sha256_of(src),
        }
        if probe_hit(rel, manifest):
            p2 += 1
        if is_binary(rel, manifest):
            p3 += 1
    state = {
        "version": "1.0",
        "generated_by": "assemble_publish.py",
        "manifest_version": manifest["version"],
        "file_count": len(files),
        "files": files,
        "forbidden": {"private_probe_hits": p2, "binary_files": p3},
    }
    write_json(os.path.join(target_abs, "PUBLISH-STATE.json"), state)
    return state


def do_apply(manifest, expected, missing, extra):
    target_abs = target_path(manifest)
    written = 0
    for rel in sorted(expected):
        src = expected[rel]["src_abs"]
        dst = os.path.join(target_abs, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        data = content_bytes(expected[rel])
        with open(dst, "wb") as fh:
            fh.write(data)
        written += 1
    deleted = 0
    for rel in extra:
        p = os.path.join(target_abs, rel)
        if os.path.exists(p):
            os.remove(p)
            deleted += 1
    prune_empty_dirs(target_abs, manifest)
    state = write_state(manifest, expected, target_abs)
    return written, deleted, state


# ---------------------------------------------------------------------------
# --check-public / --export / --assert-clean
# ---------------------------------------------------------------------------
def do_check_public(manifest, root):
    root_abs = os.path.abspath(root)
    state_path = os.path.join(root_abs, "PUBLISH-STATE.json")
    if not os.path.isfile(state_path):
        print("[check-public] FAIL: 缺少 %s" % state_path)
        return 1
    with open(state_path, encoding="utf-8") as fh:
        state = json.load(fh)
    files = state.get("files", {})
    errors = []
    for rel in sorted(files):
        p = os.path.join(root_abs, rel)
        if not os.path.isfile(p):
            errors.append("声明但缺失: %s" % rel)
            continue
        if sha256_of(p) != files[rel].get("sha256"):
            errors.append("sha256 不符: %s" % rel)
    actual = scan_actual(root_abs)
    for rel in sorted(actual):
        if rel in files:
            continue
        if is_preserve(rel, manifest) or is_never(rel, manifest):
            continue
        errors.append("未登记文件: %s" % rel)
    print("[check-public] root=%s, state_files=%d" % (root_abs, len(files)))
    for e in errors:
        print("      - %s" % e)
    print("[check-public] %s" % ("FAIL" if errors else "OK"))
    return 1 if errors else 0


def do_export(manifest, root, out_dir):
    root_abs = os.path.abspath(root)
    out_abs = os.path.abspath(out_dir)
    if os.path.abspath(root_abs) == out_abs:
        print("[export] FAIL: DIR 不能等于源根 %s" % root_abs)
        return 1
    if os.path.exists(out_abs):
        shutil.rmtree(out_abs)
    actual = scan_actual(root_abs)
    count = 0
    for rel in sorted(actual):
        if is_never(rel, manifest):
            continue
        if probe_hit(rel, manifest):
            continue
        dst = os.path.join(out_abs, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(actual[rel], dst)
        count += 1
    print("[export] %d 个文件 -> %s" % (count, out_dir))
    return 0


def do_assert_clean(manifest, d):
    d_abs = os.path.abspath(d)
    actual = scan_actual(d_abs)
    priv = [r for r in sorted(actual) if probe_hit(r, manifest)]
    bins = binary_violations(actual, manifest)
    allowed = [r for r in sorted(actual) if is_binary(r, manifest) and binary_allowed(r, manifest)]
    for r in priv:
        print("      private_probe 命中: %s" % r)
    for r in bins:
        print("      binary 违规（不在 allowlist）: %s" % r)
    for r in allowed:
        print("      binary 放行（allowlist）: %s" % r)
    ok = not priv and not bins
    print("[assert-clean] %s private=%d binary_violation=%d binary_allowed=%d"
          % ("OK" if ok else "FAIL", len(priv), len(bins), len(allowed)))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def run_emit():
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, "audit_publish.py"), "--emit"]
    print("[refresh-sanitize] %s" % " ".join(cmd))
    r = subprocess.run(cmd, cwd=MROOT)
    return r.returncode


def emit_report(manifest, expected, missing, extra, modified, pf, target_abs, as_json):
    if as_json:
        payload = {
            "expected_count": len(expected),
            "missing": missing,
            "extra": extra,
            "modified": modified,
            "preflight": {k: v for k, v in pf.items()},
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print("=" * 68)
    print("assemble_publish.py --check  ::  missing=%d extra=%d modified=%d"
          % (len(missing), len(extra), len(modified)))
    print("target = %s   expected = %d" % (target_abs, len(expected)))
    print("=" * 68)
    for label, items in (("missing（期望存在但缺失）", missing),
                         ("extra（存在但非期望非 preserve，应删）", extra),
                         ("modified（两边都有但内容不同）", modified)):
        print("\n## %s : %d" % (label, len(items)))
        for r in items:
            print("  %s" % r)
    print()
    print_preflight(pf)


def main(argv=None):
    ap = argparse.ArgumentParser(description="公开仓装配唯一入口")
    ap.add_argument("--check", action="store_true", help="对账（只读）")
    ap.add_argument("--apply", action="store_true", help="装配")
    ap.add_argument("--dry-run", action="store_true", help="配合 --apply：只打印计划")
    ap.add_argument("--check-public", action="store_true", help="CI：仅用 PUBLISH-STATE.json 校验")
    ap.add_argument("--export", metavar="DIR", help="导出 Pages 白名单")
    ap.add_argument("--assert-clean", metavar="DIR", help="断言 DIR 无私有/二进制")
    ap.add_argument("--refresh-sanitize", action="store_true", help="先跑 audit_publish.py --emit")
    ap.add_argument("--json", action="store_true", help="--check 时输出机读 JSON")
    ap.add_argument("--root", default=".", help="--check-public/--export/--assert-clean 源根")
    args = ap.parse_args(argv)

    modes = [args.check, args.apply, args.check_public,
             args.export is not None, args.assert_clean is not None]
    if sum(1 for m in modes if m) != 1:
        ap.error("必须且只能指定一个模式：--check | --apply | --check-public | --export | --assert-clean")

    if args.refresh_sanitize:
        rc = run_emit()
        if rc != 0:
            print("[refresh-sanitize] FAIL exit=%d（不继续）" % rc)
            return rc

    manifest = load_manifest()

    if args.check_public:
        return do_check_public(manifest, args.root)
    if args.export is not None:
        return do_export(manifest, args.root, args.export)
    if args.assert_clean is not None:
        return do_assert_clean(manifest, args.assert_clean)

    expected, san_missing, mir_missing = build_expected(manifest)
    pf = preflight(manifest, expected, san_missing)
    target_abs = target_path(manifest)
    missing, extra, modified = compute_diff(manifest, expected, target_abs)

    if mir_missing:
        print("[warn] mirror 声明的源路径缺失: %s" % ", ".join(mir_missing))

    if args.check:
        emit_report(manifest, expected, missing, extra, modified, pf, target_abs, args.json)
        diffs = bool(missing or extra or modified)
        return 1 if (diffs or not pf["P1"]["ok"]) else 0

    # --apply
    if args.dry_run:
        print("=" * 68)
        print("assemble_publish.py --apply --dry-run（不写盘）")
        print("target = %s   expected = %d" % (target_abs, len(expected)))
        print("计划写入/覆盖: %d   计划删除: %d" % (len(expected), len(extra)))
        print("新增(missing): %d   修改(modified): %d" % (len(missing), len(modified)))
        print("删除(extra) 路径%s:" % ("（无）" if not extra else ""))
        for r in extra:
            preserve = is_preserve(r, manifest)
            print("  %s%s" % (r, "  [preserve? 不应出现]" if preserve else ""))
        print("=" * 68)
        print_preflight(pf)
        return 0 if all(g["ok"] for g in pf.values()) else 1

    if not all(g["ok"] for g in pf.values()):
        print_preflight(pf)
        print("[apply] PREFLIGHT FAILED：不写任何字节")
        return 1

    written, deleted, state = do_apply(manifest, expected, missing, extra)
    print("[apply] 写入/覆盖 %d，删除 %d，PUBLISH-STATE.json file_count=%d"
          % (written, deleted, state["file_count"]))

    m2, e2, mo2 = compute_diff(manifest, expected, target_abs)
    if m2 or e2 or mo2:
        print("[apply] 自检 FAIL: missing=%d extra=%d modified=%d" % (len(m2), len(e2), len(mo2)))
        for r in m2:
            print("      missing: %s" % r)
        for r in e2:
            print("      extra: %s" % r)
        for r in mo2:
            print("      modified: %s" % r)
        return 1
    print("[apply] 自检 OK：--check 三类差异均为 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
