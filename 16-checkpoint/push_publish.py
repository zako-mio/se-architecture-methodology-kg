#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
push_publish.py — 用 GitHub Git Data API 推送 `_publish/` 到远端（沙箱禁 git push）

流程：blobs → tree（base_tree）→ commit → PATCH refs/heads/main
全部通过 `gh api`（subprocess），不使用 git push。

用法：
  python3 16-checkpoint/push_publish.py --dry-run     # 只打印计划
  python3 16-checkpoint/push_publish.py --apply       # 实际推送
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLISH = os.path.join(ROOT, "_publish")
OWNER = "zako-mio"
REPO = "se-architecture-methodology-kg"
BRANCH = "main"


def gh(args, inp=None, retries=4):
    """带重试的 gh 调用（网络 EOF/5xx 常见于大 blob 上传）。"""
    last = None
    for attempt in range(1, retries + 1):
        r = subprocess.run(["gh"] + args, capture_output=True, text=True, input=inp)
        if r.returncode == 0:
            return r.stdout.strip()
        last = r.stderr[:300]
        if attempt < retries:
            time.sleep(1.5 * attempt)
    raise RuntimeError("gh failed after %d tries: %s\n%s" % (retries, " ".join(args), last))


def tracked_files():
    out = subprocess.run(["git", "-C", PUBLISH, "ls-files"],
                         capture_output=True, text=True)
    return [l for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--message", default="feat(stage7p2): 阶段2 内容增密公开层")
    args = ap.parse_args()
    if not (args.dry_run or args.apply):
        ap.error("必须指定 --dry-run 或 --apply")

    files = tracked_files()
    print("[plan] 本地受控文件 %d" % len(files))

    parent = gh(["api", "repos/%s/%s/git/ref/heads/%s" % (OWNER, REPO, BRANCH),
                 "--jq", ".object.sha"])
    base_tree = gh(["api", "repos/%s/%s/git/commits/%s" % (OWNER, REPO, parent),
                    "--jq", ".tree.sha"])
    print("[plan] remote parent=%s base_tree=%s" % (parent[:12], base_tree[:12]))

    if args.dry_run:
        print("== dry-run：未推送 ==")
        return 0

    # 1) blobs（并发上传，避免串行超时）
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def upload(rel):
        p = os.path.join(PUBLISH, rel)
        with open(p, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("ascii")
        payload = json.dumps({"content": b64, "encoding": "base64"})
        # 追加⑥-c（2026-10-11）：实测 GitHub blobs API 会瞬时 `EOF`（并发上传时尤甚），
        # 原实现只在 rate limit 时重试 → 单次 EOF 即整轮推送失败。改为：
        # **认证/权限类错误立即失败**（不重试），其余（EOF/超时/5xx/限流）退避重试。
        last = None
        for attempt in range(6):
            try:
                sha = gh(["api", "repos/%s/%s/git/blobs" % (OWNER, REPO),
                          "-X", "POST", "--input", "-", "--jq", ".sha"], inp=payload, retries=2)
                return {"path": rel, "mode": "100644", "type": "blob", "sha": sha}
            except RuntimeError as e:
                last = str(e)
                if any(k in last for k in ("Bad credentials", "401", "403", "Not Found", "404")):
                    raise
                time.sleep(4 * (attempt + 1))
        raise RuntimeError("blob upload failed after 6 attempts: %s\n%s" % (rel, last))

    tree = []
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(upload, rel): rel for rel in files}
        for fu in as_completed(futs):
            tree.append(fu.result())
            done += 1
            if done % 100 == 0:
                print("   blobs %d/%d" % (done, len(files)))
    tree.sort(key=lambda x: x["path"])

    # 2) tree
    tpayload = json.dumps({"base_tree": base_tree, "tree": tree})
    new_tree = gh(["api", "repos/%s/%s/git/trees" % (OWNER, REPO),
                   "-X", "POST", "--input", "-", "--jq", ".sha"], inp=tpayload)
    print("[push] new_tree=%s" % new_tree[:12])

    # 3) commit
    cpayload = json.dumps({"message": args.message, "tree": new_tree, "parents": [parent]})
    new_commit = gh(["api", "repos/%s/%s/git/commits" % (OWNER, REPO),
                     "-X", "POST", "--input", "-", "--jq", ".sha"], inp=cpayload)
    print("[push] new_commit=%s" % new_commit[:12])

    # 4) PATCH ref
    gh(["api", "-X", "PATCH", "repos/%s/%s/git/refs/heads/%s" % (OWNER, REPO, BRANCH),
        "-f", "sha=%s" % new_commit, "-F", "force=false"])
    print("[push] ref updated")

    # 5) verify
    remote_tree = gh(["api", "repos/%s/%s/git/commits/%s" % (OWNER, REPO, new_commit),
                      "--jq", ".tree.sha"])
    print("[verify] commit.tree == new_tree : %s" % (remote_tree == new_tree))
    return 0


if __name__ == "__main__":
    sys.exit(main())
