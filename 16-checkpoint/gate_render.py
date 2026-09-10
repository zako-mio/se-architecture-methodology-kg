#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L5 render gate for the interactive DAG (13-interactive/index.html).

Renders the page in a real headless Chromium via the `agent-browser` CLI and
asserts, against the truth source `10-dag-data/methodology-dag.json`:

  * default (no hash) group view: zcount == meta.total_groups and zmode == "组级";
  * drill-down (#<group-id>): every declared group node is rendered as a member
    (member set == groups[].node_ids, member count == len(node_ids));
  * JS errors: read from an injected init-script collector (window.__jsErrors);
  * edges: read from the page-exposed runtime handle window.__cy and checked for
    dangling endpoints.

Exit code: 0 if every enabled check passes, non-zero otherwise.
A skipped check is reported as [SKIP] and NEVER counted as a pass.

Usage:
  python3 16-checkpoint/gate_render.py [--shots] [--strict-zcount] [--timeout 20]

Notes / honest caveats (verified 2026-09-10):
  * The drill-down view intentionally renders the group's member nodes PLUS
    edges-context "stub" nodes (opacity 0.55). Therefore the page's #zcount
    (cy.nodes().length) equals members + stubs and does NOT equal the group's
    node_ids length. This gate validates the *member* set (the group's declared
    nodes) as the primary correctness criterion, and reports the raw #zcount and
    stub count transparently. Use --strict-zcount to additionally require the
    literal zcount == node_ids length (expected to FAIL for drill cases).
  * `cy` is not global, but the page itself sets `window.__cy = cy`
    (13-interactive/index.html:140), so edge counts ARE retrievable.
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
DAG_JSON = REPO_ROOT / "10-dag-data" / "methodology-dag.json"
INDEX_HTML = REPO_ROOT / "13-interactive" / "index.html"
SHOTS_DIR = Path(__file__).resolve().parent / "_render-shots"
INIT_JS = Path(__file__).resolve().parent / "_gate_render_init.js"

SESSION = "gate_render"

# JS snapshot: returns a JSON string so the whole render state is read in ONE eval.
SNAPSHOT_JS = r"""
(function(){
  var out = {ok:false};
  try {
    var cy = window.__cy;
    if(!cy){ out.error = 'window.__cy is not defined (cytoscape/vendor not loaded)'; return JSON.stringify(out); }
    var zc = document.getElementById('zcount');
    var zm = document.getElementById('zmode');
    out.zcount = zc ? parseInt(zc.textContent, 10) : null;
    out.zmode = zm ? zm.textContent : null;
    out.nodes = cy.nodes().length;
    out.edges = cy.edges().length;
    var allIds = {}; cy.nodes().forEach(function(n){ allIds[n.id()] = true; });
    out.memberIds = cy.nodes().filter(function(n){ return n.data('member') === true; }).map(function(n){ return n.id(); });
    var bad = 0;
    cy.edges().forEach(function(e){ if(!allIds[e.source().id()] || !allIds[e.target().id()]) bad++; });
    out.badEdges = bad;
    out.jsErrors = (typeof window.__jsErrors !== 'undefined') ? window.__jsErrors : null;
    out.ok = true;
  } catch(e){ out.error = String(e); }
  return JSON.stringify(out);
})()
"""


def run_cmd(args, timeout, stdin_text=None):
    """Run an agent-browser command; return (rc, stdout, stderr)."""
    try:
        p = subprocess.run(
            args, input=stdin_text, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT after %ss: %s" % (timeout, " ".join(args))
    except FileNotFoundError as e:
        return 127, "", "agent-browser not found: %s" % e


def ab(*args, timeout=25, stdin_text=None):
    return run_cmd(["agent-browser", "--session", SESSION, *args], timeout, stdin_text)


def extract_json(stdout):
    """Best-effort parse of a possibly multi-line CLI output; return last JSON object."""
    txt = stdout.strip()
    if not txt:
        return None
    try:
        return json.loads(txt)
    except Exception:
        pass
    for line in reversed(txt.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except Exception:
            continue
    return None


def eval_result(js, timeout=25):
    """Run eval --json and return the parsed `result` payload (or None)."""
    rc, out, err = ab("eval", "--json", "--stdin", stdin_text=js, timeout=timeout)
    if rc != 0:
        return None, "rc=%s %s" % (rc, (err or out).strip()[:300])
    payload = extract_json(out)
    if not isinstance(payload, dict):
        return None, "non-JSON eval output: %s" % out.strip()[:300]
    if not payload.get("success", False):
        return None, "eval failed: %s" % (payload.get("error") or "")[:300]
    res = payload.get("data", {}).get("result")
    if isinstance(res, str):
        try:
            return json.loads(res), None
        except Exception as e:
            return None, "result not JSON: %s" % e
    if isinstance(res, (dict, list)):
        return res, None
    return res, None


def wait_ready(deadline):
    """Poll until the page has rendered a non-empty graph."""
    while time.time() < deadline:
        data, _ = eval_result(
            "(function(){try{var c=window.__cy;var z=document.getElementById('zcount');"
            "return JSON.stringify({cy:!!c,n:c?c.nodes().length:-1,z:z?z.textContent:null});}"
            "catch(e){return JSON.stringify({cy:false,n:-1,z:null});}})()",
            timeout=20,
        )
        if isinstance(data, dict) and data.get("cy") and (data.get("n") or 0) > 0:
            return True
        time.sleep(0.6)
    return False


def take_shot(name, timeout=30):
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOTS_DIR / ("%s.png" % name)
    rc, out, err = ab("screenshot", str(path), timeout=timeout)
    if rc == 0 and path.exists() and path.stat().st_size > 0:
        return str(path)
    return None


def set_equal(a, b):
    return set(a) == set(b)


def main():
    ap = argparse.ArgumentParser(description="L5 render gate for interactive DAG")
    ap.add_argument("--shots", action="store_true", help="save screenshots to 16-checkpoint/_render-shots/")
    ap.add_argument("--strict-zcount", action="store_true",
                    help="also require literal #zcount == group node_ids length (expects drill stubs to fail)")
    ap.add_argument("--timeout", type=int, default=25, help="per-command timeout seconds")
    args = ap.parse_args()

    print("=" * 72)
    print("L5 render gate (headless Chromium via agent-browser)")
    print("  repo root : %s" % REPO_ROOT)
    print("  page      : %s" % INDEX_HTML)
    print("  truth     : %s" % DAG_JSON)
    print("  time      : %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 72)

    failures = []
    skips = []

    # --- environment -------------------------------------------------------
    if shutil.which("agent-browser") is None:
        print("[SKIP] agent-browser CLI not found on PATH")
        print("render gate: FAIL (environment missing: agent-browser)")
        return 2
    if not INDEX_HTML.exists():
        print("[FAIL] page not found: %s" % INDEX_HTML)
        print("render gate: FAIL")
        return 2

    # --- truth source ------------------------------------------------------
    try:
        dag = json.loads(DAG_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        print("[FAIL] cannot read truth DAG: %s" % e)
        print("render gate: FAIL")
        return 2
    meta = dag.get("meta", {})
    total_nodes = meta.get("total_nodes")
    total_groups = meta.get("total_groups")
    groups = dag.get("groups", [])
    by_id = {g["id"]: g for g in groups}
    print("truth: total_nodes=%s total_groups=%s groups=%d" % (total_nodes, total_groups, len(groups)))

    if total_groups != len(groups):
        failures.append("meta.total_groups (%s) != len(groups) (%d)" % (total_groups, len(groups)))
    actual_nodes = len(dag.get("nodes", []))
    if total_nodes != actual_nodes:
        failures.append("meta.total_nodes (%s) != len(nodes) (%d)" % (total_nodes, actual_nodes))

    # init-script that records JS errors on every document
    INIT_JS.write_text(
        "window.__jsErrors = [];\n"
        "window.addEventListener('error', function(e){ try{ window.__jsErrors.push(String(e.message)); }catch(_){} });\n"
        "window.addEventListener('unhandledrejection', function(e){ try{ window.__jsErrors.push('unhandledrejection: '+String(e.reason)); }catch(_){} });\n",
        encoding="utf-8",
    )

    base_url = INDEX_HTML.resolve().as_uri()

    # cases: (label, hash, expected_node_ids_or_None)
    drill_defs = ["GL-ESSENCE", "GL-METHOD", "GL-TECHNOLOGY", "GC-CASE", "GD-G", "GD-F"]
    cases = [("default", None, None)]
    for gid in drill_defs:
        if gid not in by_id:
            failures.append("drill group %s missing from truth groups[]" % gid)
            continue
        cases.append((gid, gid, list(by_id[gid]["node_ids"])))

    js_error_state = "ok"          # ok | fail | skipped
    js_error_detail = []
    edges_state = "ok"             # ok | unverified
    case_results = {}
    raw_lines = []

    def log(line):
        print(line)
        raw_lines.append(line)

    try:
        for label, gid, expect_ids in cases:
            url = base_url if gid is None else (base_url + "#" + gid)
            rc, out, err = ab("open", url, "--init-script", str(INIT_JS), timeout=args.timeout + 15)
            if rc != 0:
                log("[FAIL] %-14s open failed rc=%s %s" % (label, rc, (err or out).strip()[:200]))
                failures.append("%s: open failed" % label)
                case_results[label] = {"result": "FAIL", "error": "open failed"}
                continue

            ready = wait_ready(time.time() + args.timeout)
            if not ready:
                log("[FAIL] %-14s render never became ready (timeout %ss)" % (label, args.timeout))
                failures.append("%s: render timeout" % label)
                case_results[label] = {"result": "FAIL", "error": "render timeout"}
                continue

            data, e = eval_result(SNAPSHOT_JS, timeout=args.timeout)
            if not isinstance(data, dict) or not data.get("ok"):
                msg = (data or {}).get("error") if isinstance(data, dict) else e
                log("[FAIL] %-14s snapshot eval failed: %s" % (label, msg))
                failures.append("%s: snapshot failed (%s)" % (label, msg))
                case_results[label] = {"result": "FAIL", "error": str(msg)}
                continue

            zcount = data.get("zcount")
            zmode = data.get("zmode")
            member_ids = data.get("memberIds") or []
            edges_n = data.get("edges")
            bad_edges = data.get("badEdges")

            # JS error check
            jse = data.get("jsErrors")
            if jse is None:
                js_error_state = "skipped"
            elif jse:
                js_error_state = "fail"
                js_error_detail.extend(jse[:10])

            if bad_edges:
                edges_state = "fail" if edges_state == "ok" else edges_state

            if gid is None:
                # default group view
                ok = (zcount == total_groups) and (zmode == "组级")
                status = "PASS" if ok else "FAIL"
                detail = "zcount=%s (expect %s) zmode=%r (expect '组级') edges=%s" % (
                    zcount, total_groups, zmode, edges_n)
                if not ok:
                    failures.append("default: %s" % detail)
                case_results[label] = {
                    "mode": zmode, "zcount": zcount, "expect": total_groups,
                    "edges": edges_n, "result": status,
                }
            else:
                expected = list(expect_ids)
                member_ok = set_equal(member_ids, expected) and (len(member_ids) == len(expected))
                stub = (data.get("nodes") or 0) - len(member_ids)
                strict_ok = (zcount == len(expected))
                ok = member_ok and (strict_ok if args.strict_zcount else True)
                status = "PASS" if ok else "FAIL"
                detail = ("members=%d/%d set_match=%s | zcount=%s stubs=%s | edges=%s"
                          % (len(member_ids), len(expected), set_equal(member_ids, expected),
                             zcount, stub, edges_n))
                if not ok:
                    missing = sorted(set(expected) - set(member_ids))[:6]
                    extra = sorted(set(member_ids) - set(expected))[:6]
                    failures.append("%s: %s missing=%s extra=%s" % (label, detail, missing, extra))
                case_results[label] = {
                    "mode": zmode, "member": len(member_ids), "expect": len(expected),
                    "member_set_match": set_equal(member_ids, expected),
                    "zcount": zcount, "stubs": stub, "edges": edges_n, "result": status,
                }
            log("[%s] %-14s %s" % (status, label, detail))

            if args.shots and label in ("default", "GL-ESSENCE"):
                shot = take_shot(label)
                log("        shot: %s" % (shot or "FAILED"))

        # explicit note about the stub semantics of #zcount
        log("")
        log("[INFO] drill-down #zcount = member nodes + edge-context stub nodes "
            "(13-interactive/index.html buildGroupDrill). Gate validates the member set.")
    finally:
        rc, out, err = ab("close", timeout=20)
        if rc != 0:
            run_cmd(["agent-browser", "--session", SESSION, "close", "--all"], 15)
        try:
            if INIT_JS.exists():
                os.remove(INIT_JS)
        except OSError:
            pass

    # --- JS error / edge verdicts -----------------------------------------
    log("")
    if js_error_state == "ok":
        log("[PASS] js-errors      no JS errors captured (window.__jsErrors == [])")
    elif js_error_state == "fail":
        log("[FAIL] js-errors      %d JS error(s): %s" % (len(js_error_detail), js_error_detail))
        failures.append("JS errors: %s" % js_error_detail)
    else:
        log("[SKIP] js-errors      window.__jsErrors unavailable — NOT a pass")
        skips.append("js-errors")

    if edges_state == "ok":
        log("[PASS] edges          runtime handle window.__cy exposed; all edge endpoints resolve, 0 dangling")
    else:
        log("[FAIL] edges          %s" % edges_state)
        failures.append("dangling edge endpoints")

    # --- summary -----------------------------------------------------------
    log("")
    log("-" * 72)
    if failures:
        log("render gate: FAIL (%d issue(s), %d skipped)" % (len(failures), len(skips)))
        for f in failures:
            log("  - %s" % f)
        code = 1
    else:
        log("render gate: PASS (all %d cases; skipped=%d)" % (len(cases), len(skips)))
        code = 0
    log("-" * 72)

    return code


if __name__ == "__main__":
    sys.exit(main())
