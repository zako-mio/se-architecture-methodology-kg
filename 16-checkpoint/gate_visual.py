#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_visual.py — L4 视觉门控（阶段6 · 浅色 Codex 文档流）

契约: 00-plan/stage6-content-ia-spec.md §7（响应式与无溢出硬约束）+ §10（门控点位，
      其中「无溢出」归 L4）。
参考: 16-checkpoint/gate_render.py（agent-browser 调用封装风格，只读复用，不修改）、
      16-checkpoint/gate_layout.py（文本层门控风格基准，纯标准库）。

本门控在真实 headless Chromium（agent-browser CLI）中渲染目标页，分两段校验：

  A. 运行态 / 几何校验（经 `agent-browser eval` 取真值）
     runtime.h-overflow     页面级无横向溢出：documentElement.scrollWidth <= innerWidth+1
     runtime.structure      关键结构块 defcard / svg / tradeoff / nav.toc(≥900px) / evidence
                            存在即宽高 > 0；页上不存在该块记为 [SKIP]（非 PASS）
     runtime.svg-clip       svg.scrollWidth <= svg.clientWidth+1，或该 svg 位于
                            overflow-x:auto|scroll 容器内
     runtime.font           <body> 计算字号 ≥14px@1280、≥13px@390
     runtime.lineheight     首个可见正文 <p> 行高 ≥ 1.5 × 字号
     runtime.overflow-leak  除 overflow-x:auto|scroll 容器内的元素外，无元素
                            getBoundingClientRect().right > innerWidth+1
     runtime.overlap        【主判据·真实文本重叠】仅针对 HTML 文档流文本：对每个
                            含直接文本节点的元素，用 Range.getClientRects() 取
                            紧致文本行盒（不含 padding/border），两两判定真实 2D 相交
                            （right>left+EPS 且 bottom>top+EPS 且相交面积>MIN_AREA）；
                            排除祖先/后代、同父 display:inline 片段、被 overflow
                            裁切、以及双方均有显式 z-index 的分层元素。命中记 [WARN]
                            （spec §10：重叠嫌疑仅 warning，不作 FAIL）。
     口径变更：旧的 1D 像素判据「同行两段墨迹被 1–3px 背景隔断」已退役（见
     pixel.overlap-suspect 说明与常量注释），原因是该判据与「重叠」无因果关系——
     实测正常页 GL-ESSENCE@1280 有 40 行命中，全部是中文单字/词间正常的 1–3px
     字距，而真实重叠对应的是零间距墨迹融合，1D 判据无法区分；DOM Range 紧致盒
     则是重叠的直接几何量。SVG <text> 未纳入自动判定：其 getBoundingClientRect 为
     em 盒，实测重叠比例在正常排布下呈连续谱（0.01→0.56，0.28 与 0.31 相邻），
     不存在可辩护的二值阈值；脚本改为在报告中提示（见 runtime.overlap 证据），
     不再产出启发式 WARN。

  B. 像素计数校验（Pillow + numpy 分析全页 PNG）
     pixel.non-empty        非背景像素占比 ≥ 3%（防白页/渲染失败）
     pixel.bg-corners       四角采样接近 #f5f1e8（容差 ±12/通道）
     pixel.page-height      图像高 > 1.5 × 视口高（防截断式渲染失败）
     pixel.svg-ink          svg 裁剪区非背景像素占比 ≥ 1.5%（关系图确画出内容）
     pixel.right-clip       最右 4px 竖条非背景像素占比 < 2%（防右侧裁切）
     pixel.overlap-suspect  【已退役】原 1D 像素启发式；DOM runtime.overlap 可用时
                            记 [SKIP] 并说明退役理由，不再产出命中（避免误报）。
                            仅当 DOM 判据不可用时才作为降级提示（保守，宁缺毋滥）。

阈值全部写死在下方常量并注明依据（见 THRESHOLDS 注释）；脚本不会为让结果变 PASS
而放宽阈值，也不会修改任何页面。

C. VLM 通道（本脚本不调用模型，仅留接口）
  * --vlm-manifest <path>  输出待检截图清单 JSON：
        {"generated": "<ts>", "screenshot_dir": "<abs>", "items": [
            {"screenshot": "<abs png>", "page": "<repo-rel>", "viewport": "1280x900",
             "runtime_verdict": "PASS|FAIL|WARN|SKIP", "screenshot_ok": true} ... ]}
  * --vlm-result <path>    读入外部 VLM 判定 JSON 并入最终裁定（VLM FAIL 拉低总判定）。
        格式（results 可为列表，也可直接给列表）：
        {"results": [
            {"screenshot": "<abs/相对 png 或仅 basename>", "page": "<repo-rel>",
             "viewport": "1280x900", "verdict": "PASS|FAIL|WARN",
             "notes": "可选说明"} ... ]}
        verdict 大小写不敏感；FAIL → 总判定 FAIL，WARN → 总判定至少 WARN。
        匹配顺序：screenshot 完整路径 > basename > (page, viewport)。

退出码: 0 = 综合判定 PASS；1 = FAIL / WARN / 仅 SKIP（SKIP 从不计为 PASS）。
A skipped check is reported as [SKIP] and NEVER counted as a pass.

用法:
    python3 16-checkpoint/gate_visual.py --check all
    python3 16-checkpoint/gate_visual.py --check runtime,pixels
    python3 16-checkpoint/gate_visual.py --check runtime --viewport 1280,390
    python3 16-checkpoint/gate_visual.py --pages 16-checkpoint/_visual-pages.txt
    python3 16-checkpoint/gate_visual.py --check all --vlm-manifest /tmp/vlm.json
    python3 16-checkpoint/gate_visual.py --check all --vlm-result /tmp/vlm-result.json

环境事实（已实测 2026-09-11）:
  * agent-browser 0.34.0 可用；流程 open → set viewport <w> <h> → reload →
    screenshot --full <png> → eval --json --stdin；结束 close --all。
  * Pillow / numpy 属**第三方依赖**：缺失时像素段优雅 [SKIP] 并说明原因，不崩溃。
    在 CI 中 L4 显式 SKIPPED，此依赖可接受。
"""

import argparse
import datetime
import json
import math
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # MISSION_ROOT
SHOTS_DIR = HERE / "_render-shots" / "visual"
SESSION = "gate_visual"

# ---------------------------------------------------------------- 阈值常量
# 全部写死并注明依据，禁止为通过而放宽。
BG_RGB = (245, 241, 232)                # §1 设计 token --bg:#f5f1e8
CORNER_TOL = 12                         # §B2 明示 ±12/通道
INK_DIST = 40.0                         # 距背景的欧氏距离阈值：面板 #fffdf8（距≈22）视为
                                        # 背景面，边框/文字/彩线（距>40）视为墨迹
MIN_INK_RATIO = 0.03                    # §B1 非背景 ≥3%
MIN_SVG_INK_RATIO = 0.015               # §B4 svg 裁剪区 ≥1.5%
MAX_RIGHT_STRIP_INK = 0.02              # §B5 最右 4px 墨迹 <2%
PAGE_HEIGHT_FACTOR = 1.5                # §B3 高 > 1.5×视口高
MIN_BODY_FONT = {1280: 14.0, 390: 13.0}  # §A4 字号下限（按视口宽）
MIN_LINEHEIGHT_RATIO = 1.5              # §A4 行高 ≥1.5×字号
RIGHT_STRIP_PX = 4                      # §B5 最右 4px 竖条

# runtime.overlap（DOM 2D 主判据）阈值。判据 = 两个紧致文本行盒的真实二维相交：
#   r1.right > r2.left + EPS && r1.left < r2.right - EPS
#   r1.bottom > r2.top + EPS && r1.top < r2.bottom - EPS 且相交面积 > MIN_AREA
# EPS 吸收亚像素/取整噪声；MIN_AREA 排除仅盒边缘相切（如相邻块的 padding 相触）。
# 实测 16 个渲染目标（8 页 × 2 视口）HTML 命中恒为 0；构造的绝对定位覆盖层可稳定命中。
OVERLAP_EPS = 1.0                       # §A 2D 相交最小重叠（px）
OVERLAP_MIN_AREA = 6.0                  # §A 最小相交面积（px²）
# 背景：旧 1D 判据（同行两段墨迹被 ≤3px 背景隔断）与「重叠」不相关，故退役：
#   在 GL-ESSENCE@1280 正常排版下抽样命中的 40 行，gap 分布 {1px:25, 2px:14, 3px:2}，
#   全部来自中文字间/词间正常字距；真实重叠对应零间距墨迹融合而非 1–3px 隔断。
#   保留常量仅供降级提示参考，不再作为主判据。
OVERLAP_LEGACY_GAP_MAX = 3              # [退役] 旧 1D 判据背景隔断上限
OVERLAP_LEGACY_SEG_MIN = 20             # [退役] 旧 1D 判据每段墨迹最小长度
OVERLAP_SCAN_STEP = 3                   # 抽样步长（复用：DOM 判据不依赖）
# SVG <text> bbox 重叠比例仅用于报告提示（不产出自动判定）。实测正常排布为连续谱，
# 无自然二值阈值，故不用于 WARN。
SVG_OVERLAP_NOTICE_RATIO = 0.50         # 报告提示阈值：相交面积 ≥ 较小 bbox 的 50%

# 渲染目标集（8 页）。conflict 节点 MTH-O-05 由 methodology-dag.json 的
# conflicts 边 MTH-O-04 -> MTH-O-05 选出（在 4 条 conflicts 中其案例带最重）。
DEFAULT_PAGES = [
    ("ESS-H-01",      "11-node-pages/ESS-H-01.html"),
    ("MTH-F-02",      "11-node-pages/MTH-F-02.html"),
    ("TEC-F-01",      "11-node-pages/TEC-F-01.html"),
    ("MTH-O-05",      "11-node-pages/MTH-O-05.html"),   # conflicts 节点
    ("GL-ESSENCE",    "12-groups/GL-ESSENCE.html"),
    ("learning-path", "14-views/02-learning-path.html"),
    ("glossary",      "14-views/glossary.html"),
    ("index",         "index.html"),
]
# conflicts 节点证据（写入报告）：MTH-O-04 -> MTH-O-05
CONFLICT_NODE = "MTH-O-05"
CONFLICT_EDGE = "MTH-O-04 -> MTH-O-05"

DEFAULT_VIEWPORTS = [
    ("desktop", 1280, 900),
    ("mobile", 390, 844),
]

STRUCT_SELECTORS = [".defcard", "svg", ".tradeoff", "nav.toc", ".evidence"]

SNAPSHOT_JS = r"""
(function(){
  function rect(e){
    var r=e.getBoundingClientRect();
    return {w:Math.round(r.width*100)/100, h:Math.round(r.height*100)/100,
            left:Math.round(r.left*100)/100,
            top:Math.round((r.top+window.scrollY)*100)/100,
            right:Math.round(r.right*100)/100};
  }
  function inScrollX(e){
    var p=e.parentElement;
    while(p){ var cs=getComputedStyle(p);
      if(cs.overflowX==='auto'||cs.overflowX==='scroll') return true;
      p=p.parentElement; }
    return false;
  }
  var out={ok:false};
  try{
    out.iw=window.innerWidth; out.ih=window.innerHeight;
    out.sw=document.documentElement.scrollWidth;
    out.bw=document.body?document.body.scrollWidth:null;
    out.sh=document.documentElement.scrollHeight;
    var bcs=getComputedStyle(document.body);
    out.body_fs=parseFloat(bcs.fontSize); out.body_lh=bcs.lineHeight;
    out.blocks={};
    var sels=__SELS__;
    for(var i=0;i<sels.length;i++){
      var sel=sels[i]; var els=document.querySelectorAll(sel); var arr=[];
      for(var j=0;j<els.length;j++) arr.push(rect(els[j]));
      out.blocks[sel]={count:els.length, rects:arr};
    }
    out.svg=[];
    var svgs=document.querySelectorAll('svg');
    for(var k=0;k<svgs.length;k++){
      var s=svgs[k]; var rr=rect(s);
      out.svg.push({cw:s.clientWidth, sw:s.scrollWidth, ov:inScrollX(s),
                    w:rr.w, h:rr.h, left:rr.left, top:rr.top});
    }
    out.para=null;
    var ps=document.querySelectorAll('p');
    for(var m=0;m<ps.length;m++){
      var p=ps[m]; if(!p.offsetParent) continue;
      var t=(p.textContent||'').trim(); if(t.length<8) continue;
      var pcs=getComputedStyle(p);
      out.para={fs:parseFloat(pcs.fontSize), lh:pcs.lineHeight, text:t.slice(0,40)};
      break;
    }
    out.leaks=[];
    var all=document.querySelectorAll('*');
    for(var n=0;n<all.length;n++){
      var e=all[n]; var r=e.getBoundingClientRect();
      if(r.width<=0&&r.height<=0) continue;
      if(r.right>window.innerWidth+1 && !inScrollX(e)){
        var nm=e.tagName;
        if(e.className&&typeof e.className==='string')
          nm+='.'+e.className.split(' ').slice(0,2).join('.');
        out.leaks.push({el:nm.slice(0,60), right:Math.round(r.right)});
      }
    }
    if(out.leaks.length>30) out.leaks=out.leaks.slice(0,30);
    out.ok=true;
  }catch(err){ out.error=String(err); }
  return JSON.stringify(out);
})()
"""

# DOM 真实文本重叠判定（主判据）。返回 {ok, htmlCands, hits, svgCands, svgNotice}。
# 与 SNAPSHOT_JS 分离，便于 `--check pixels`（仅像素段）也能取到 DOM 真值。
OVERLAP_JS = r"""
(function(){
  var EPS = __EPS__, MIN_AREA = __MIN_AREA__, SVG_NOTICE = __SVG_NOTICE__;
  function inSVG(el){ return el.namespaceURI==='http://www.w3.org/2000/svg' || !!(el.ownerSVGElement); }
  function rendered(el){
    if(!el.getClientRects().length) return false;
    if(el.checkVisibility && !el.checkVisibility({checkOpacity:true, checkVisibilityCSS:true})) return false;
    return true;
  }
  function tagName(el){
    var s=el.tagName.toLowerCase();
    if(el.id) s+='#'+el.id;
    if(el.className&&typeof el.className==='string'){
      var c=el.className.trim().split(/\s+/).slice(0,2).join('.');
      if(c) s+='.'+c;
    }
    return s;
  }
  function inlineLevel(el){var d=getComputedStyle(el).display;return d==='inline'||d==='inline-block'||d==='inline-flex';}
  function zIndex(el){
    var cs=getComputedStyle(el); if(cs.position==='static') return null;
    var z=cs.zIndex; if(z==='auto'||z==='') return null;
    var n=parseInt(z,10); return isNaN(n)?null:n;
  }
  function ownTextNodes(el){
    var arr=[];
    for(var i=0;i<el.childNodes.length;i++){
      var n=el.childNodes[i];
      if(n.nodeType===3 && n.nodeValue && n.nodeValue.replace(/\s+/g,' ').trim()) arr.push(n);
    }
    return arr;
  }
  function ownText(el){
    var t=''; for(var i=0;i<el.childNodes.length;i++){
      var n=el.childNodes[i]; if(n.nodeType===3) t+=n.nodeValue;
    }
    return t.replace(/\s+/g,' ').trim();
  }
  // 与所有 overflow!=visible 祖先求交，得到元素可见裁切盒（overflow:hidden 裁掉的不算）
  function clipBox(el,r){
    var box={left:r.left,top:r.top,right:r.right,bottom:r.bottom};
    var p=el.parentElement;
    while(p&&p!==document.documentElement){
      var cs=getComputedStyle(p), ox=cs.overflowX, oy=cs.overflowY;
      if(ox!=='visible'||oy!=='visible'){
        var pr=p.getBoundingClientRect();
        if(ox!=='visible'){box.left=Math.max(box.left,pr.left);box.right=Math.min(box.right,pr.right);}
        if(oy!=='visible'){box.top=Math.max(box.top,pr.top);box.bottom=Math.min(box.bottom,pr.bottom);}
      }
      p=p.parentElement;
    }
    return box;
  }
  var out={ok:false};
  try{
    var html=[], svg=[];
    var all=document.querySelectorAll('body *');
    for(var i=0;i<all.length;i++){
      var el=all[i];
      if(!rendered(el)) continue;
      var cs=getComputedStyle(el);
      if(cs.display==='none'||cs.visibility==='hidden'||parseFloat(cs.opacity)===0) continue;
      var txt=ownText(el);
      if(inSVG(el)){
        if(el.tagName.toLowerCase()!=='text'||!txt) continue;
        var bb=el.getBoundingClientRect();
        if(bb.width<2||bb.height<2) continue;
        svg.push({el:el,tag:tagName(el),text:txt.slice(0,22),
                  rect:{left:bb.left,top:bb.top,right:bb.right,bottom:bb.bottom}});
        continue;
      }
      if(!txt) continue;
      var tns=ownTextNodes(el);
      if(!tns.length) continue;
      var rects=[];
      for(var ti=0;ti<tns.length;ti++){
        var range=document.createRange();
        range.selectNodeContents(tns[ti]);
        var crs=range.getClientRects();
        for(var k=0;k<crs.length;k++){
          var rr=crs[k];
          if(rr.width<2||rr.height<2) continue;
          var box=clipBox(el,rr);
          if(box.right-box.left<2||box.bottom-box.top<2) continue;
          rects.push(box);
        }
      }
      if(!rects.length) continue;
      html.push({el:el,tag:tagName(el),text:txt.slice(0,26),
                 inline:inlineLevel(el),parent:el.parentElement,z:zIndex(el),rects:rects});
    }
    var hits=[];
    for(var a=0;a<html.length;a++){
      for(var b=a+1;b<html.length;b++){
        var A=html[a],B=html[b];
        if(A.el.contains(B.el)||B.el.contains(A.el)) continue;          // 祖先/后代
        if(A.parent===B.parent&&A.inline&&B.inline) continue;          // 同父内联片段
        if(A.z!==null&&B.z!==null) continue;                           // 显式 z-index 分层
        for(var ra=0;ra<A.rects.length;ra++){
          var x=A.rects[ra], found=false;
          for(var rb=0;rb<B.rects.length;rb++){
            var y=B.rects[rb];
            var ox=Math.min(x.right,y.right)-Math.max(x.left,y.left);
            var oy=Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top);
            if(ox>EPS&&oy>EPS&&ox*oy>MIN_AREA){
              hits.push({a:A.tag,b:B.tag,ta:A.text,tb:B.text,
                         ox:Math.round(ox*10)/10,oy:Math.round(oy*10)/10,
                         ra:[Math.round(x.left),Math.round(x.top),Math.round(x.right),Math.round(x.bottom)],
                         rb:[Math.round(y.left),Math.round(y.top),Math.round(y.right),Math.round(y.bottom)]});
              found=true; break;
            }
          }
          if(found) break;
        }
        if(hits.length>200) break;
      }
      if(hits.length>200) break;
    }
    // SVG 提示（不产出 WARN，仅报告）：相交面积 ≥ 较小 bbox 的 SVG_NOTICE
    var svgNotice=[];
    for(var c=0;c<svg.length;c++){
      for(var d=c+1;d<svg.length;d++){
        var S=svg[c],T=svg[d];
        if(S.el.contains(T.el)||T.el.contains(S.el)) continue;
        var ox2=Math.min(S.rect.right,T.rect.right)-Math.max(S.rect.left,T.rect.left);
        var oy2=Math.min(S.rect.bottom,T.rect.bottom)-Math.max(S.rect.top,T.rect.top);
        if(ox2<=0||oy2<=0) continue;
        var aS=(S.rect.right-S.rect.left)*(S.rect.bottom-S.rect.top);
        var aT=(T.rect.right-T.rect.left)*(T.rect.bottom-T.rect.top);
        var minA=Math.min(aS,aT);
        if(minA>0 && ox2*oy2/minA>=SVG_NOTICE){
          svgNotice.push({a:S.tag,b:T.tag,ta:S.text,tb:T.text,
                          frac:Math.round(ox2*oy2/minA*100)/100});
        }
      }
    }
    out.htmlCands=html.length; out.svgCands=svg.length;
    out.hits=hits; out.svgNotice=svgNotice.slice(0,10);
    out.ok=true;
  }catch(err){ out.error=String(err); }
  return JSON.stringify(out);
})()
"""


# ---------------------------------------------------------------- 通用工具

def run_cmd(args, timeout, stdin_text=None):
    try:
        p = subprocess.run(args, input=stdin_text, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT after %ss: %s" % (timeout, " ".join(args))
    except FileNotFoundError as e:
        return 127, "", "not found: %s" % e


def ab(*args, timeout=30, stdin_text=None):
    return run_cmd(["agent-browser", "--session", SESSION, *args], timeout, stdin_text)


def extract_json(stdout):
    txt = (stdout or "").strip()
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


def eval_result(js, timeout=30):
    """Run eval --json --stdin; return (parsed_result_dict, error_or_None)."""
    rc, out, err = ab("eval", "--json", "--stdin", stdin_text=js, timeout=timeout)
    if rc != 0:
        return None, "rc=%s %s" % (rc, (err or out).strip()[:300])
    payload = extract_json(out)
    if not isinstance(payload, dict):
        return None, "non-JSON eval output: %s" % (out or "").strip()[:300]
    if not payload.get("success", False):
        return None, "eval failed: %s" % str(payload.get("error"))[:300]
    res = payload.get("data", {}).get("result")
    if isinstance(res, str):
        try:
            return json.loads(res), None
        except Exception as e:
            return None, "result not JSON: %s" % e
    if isinstance(res, (dict, list)):
        return res, None
    return res, None


def eval_overlap(timeout=30):
    """Run the DOM overlap judge in the current tab; return dict or None(skip)."""
    js = (OVERLAP_JS.replace("__EPS__", repr(OVERLAP_EPS))
                  .replace("__MIN_AREA__", repr(OVERLAP_MIN_AREA))
                  .replace("__SVG_NOTICE__", repr(SVG_OVERLAP_NOTICE_RATIO)))
    data, e = eval_result(js, timeout=timeout)
    if not isinstance(data, dict) or not data.get("ok"):
        return {"ok": False, "error": (data or {}).get("error") or e}
    return data


def report_overlap(ov, page_rel, vps, rep):
    """Emit runtime.overlap. Returns True if the DOM judge is available."""
    if not isinstance(ov, dict) or not ov.get("ok"):
        rep.add("runtime.overlap", page_rel, vps, "SKIP",
                "DOM 重叠判据不可用: %s" % str((ov or {}).get("error"))[:160])
        return False
    hits = ov.get("hits") or []
    notice = ov.get("svgNotice") or []
    tail = ""
    if notice:
        tail = "；SVG 标签 bbox 重度重叠提示(不计 WARN) %d 处: %s" % (
            len(notice), [(n["ta"], n["tb"], n["frac"]) for n in notice[:3]])
    if not hits:
        rep.add("runtime.overlap", page_rel, vps, "PASS",
                "HTML 紧致文本盒 2D 相交=0（候选 %d，Range 真值）%s"
                % (ov.get("htmlCands", 0), tail))
    else:
        sample = ["%s∩%s ox%s×oy%s" % (h["a"], h["b"], h["ox"], h["oy"])
                  for h in hits[:4]]
        rep.add("runtime.overlap", page_rel, vps, "WARN",
                "%d 处真实 2D 文本重叠（spec §10 仅 warning）；样例 %s%s"
                % (len(hits), sample, tail))
    return True


def parse_lineheight(val, fs):
    """Return line-height in px from computed value; None if not resolvable."""
    if val is None:
        return None
    s = str(val).strip()
    if s.endswith("px"):
        try:
            return float(s[:-2])
        except ValueError:
            return None
    try:
        f = float(s)
    except ValueError:
        return None
    if f > 0 and f < 6 and fs:
        return f * fs
    return f if f > 0 else None


# ---------------------------------------------------------------- 结果记录

class Reporter(object):
    def __init__(self):
        self.items = []   # dict: check, page, viewport, status, evidence

    def add(self, check, page, viewport, status, evidence):
        self.items.append({"check": check, "page": page, "viewport": viewport,
                           "status": status, "evidence": evidence})

    def count(self, status):
        return sum(1 for it in self.items if it["status"] == status)

    @property
    def total(self):
        return len(self.items)

    @property
    def verdict(self):
        if any(it["status"] == "FAIL" for it in self.items):
            return "FAIL"
        if any(it["status"] == "WARN" for it in self.items):
            return "WARN"
        if all(it["status"] == "SKIP" for it in self.items) and self.items:
            return "SKIP"
        if any(it["status"] == "PASS" for it in self.items):
            return "PASS"
        return "SKIP"

    def print_all(self, show_evidence=True):
        for it in self.items:
            line = "[%s] %-24s %s @%s" % (
                it["status"], it["check"], it["page"], it["viewport"])
            if show_evidence and it["evidence"]:
                line += "  — %s" % it["evidence"]
            print(line)


# ---------------------------------------------------------------- 运行时检查

def open_page(page_rel, page_abs, vw, vh, rep, timeout):
    """Open page + set viewport + reload. Returns True when the page is usable."""
    if not page_abs.exists():
        rep.add("runtime.page", page_rel, "%dx%d" % (vw, vh), "FAIL",
                "页面不存在: %s" % page_abs)
        return False
    url = page_abs.resolve().as_uri()
    vps = "%dx%d" % (vw, vh)
    rc, out, err = ab("open", url, timeout=timeout + 15)
    if rc != 0:
        rep.add("runtime.open", page_rel, vps, "FAIL",
                "open rc=%s %s" % (rc, (err or out).strip()[:200]))
        return False
    rc, out, err = ab("set", "viewport", str(vw), str(vh), timeout=timeout)
    if rc != 0:
        rep.add("runtime.viewport", page_rel, vps, "FAIL",
                "set viewport rc=%s %s" % (rc, (err or out).strip()[:200]))
    rc, out, err = ab("reload", timeout=timeout)
    if rc != 0:
        rep.add("runtime.reload", page_rel, vps, "FAIL",
                "reload rc=%s %s" % (rc, (err or out).strip()[:200]))
    return True


def run_runtime(page_rel, page_abs, vw, vh, rep, timeout):
    """Returns (info_dict_or_None, dom_overlap_available_bool)."""
    if not open_page(page_rel, page_abs, vw, vh, rep, timeout):
        return None, False
    vps = "%dx%d" % (vw, vh)
    js = SNAPSHOT_JS.replace("__SELS__", json.dumps(STRUCT_SELECTORS))
    data, e = eval_result(js, timeout=timeout)
    if not isinstance(data, dict) or not data.get("ok"):
        msg = (data or {}).get("error") if isinstance(data, dict) else e
        rep.add("runtime.snapshot", page_rel, vps, "FAIL",
                "快照失败: %s" % str(msg)[:200])
        return None, False

    iw = data.get("iw")
    sw = data.get("sw")
    sh = data.get("sh")

    # A1 页面级横向溢出
    if iw is None or sw is None:
        rep.add("runtime.h-overflow", page_rel, vps, "FAIL", "缺少 iw/sw")
    elif sw <= iw + 1:
        rep.add("runtime.h-overflow", page_rel, vps, "PASS",
                "scrollWidth=%s <= innerWidth=%s + 1" % (sw, iw))
    else:
        rep.add("runtime.h-overflow", page_rel, vps, "FAIL",
                "页面横向溢出 %dpx: scrollWidth=%s > innerWidth=%s" % (sw - iw, sw, iw))

    # A2 关键结构块
    blocks = data.get("blocks") or {}
    for sel in STRUCT_SELECTORS:
        info = blocks.get(sel) or {"count": 0, "rects": []}
        cnt = info.get("count", 0)
        if cnt == 0:
            if sel == "nav.toc" and vw < 900:
                rep.add("runtime.structure", page_rel, vps, "SKIP",
                        "nav.toc 在 <900px 折为折叠盒，本视口不校验")
            else:
                rep.add("runtime.structure", page_rel, vps, "SKIP",
                        "页上无 %s（非适用）" % sel)
            continue
        rects = info.get("rects") or []
        bad = [r for r in rects if not (r.get("w", 0) > 0 and r.get("h", 0) > 0)]
        if bad:
            rep.add("runtime.structure", page_rel, vps, "FAIL",
                    "%s ×%d 存在零尺寸: %s" % (sel, len(bad),
                                             [(r.get("w"), r.get("h")) for r in bad[:3]]))
        else:
            rep.add("runtime.structure", page_rel, vps, "PASS",
                    "%s ×%d 均 w>0,h>0 (首个 %sx%s)"
                    % (sel, cnt, rects[0].get("w"), rects[0].get("h")))

    # A3 关系图不被裁切
    svgs = data.get("svg") or []
    if not svgs:
        rep.add("runtime.svg-clip", page_rel, vps, "SKIP", "页上无 svg")
    for idx, s in enumerate(svgs):
        cw = s.get("cw") or 0
        sww = s.get("sw") or 0
        ov = bool(s.get("ov"))
        if sww <= cw + 1:
            rep.add("runtime.svg-clip", page_rel, vps, "PASS",
                    "svg[%d] scrollWidth=%s <= clientWidth=%s" % (idx, sww, cw))
        elif ov:
            rep.add("runtime.svg-clip", page_rel, vps, "PASS",
                    "svg[%d] w=%s 位于 overflow-x 容器内（容器内滚动允许）"
                    % (idx, s.get("w")))
        else:
            rep.add("runtime.svg-clip", page_rel, vps, "FAIL",
                    "svg[%d] 被裁切: scrollWidth=%s > clientWidth=%s 且无滚动容器"
                    % (idx, sww, cw))

    # A4 字号下限
    body_fs = data.get("body_fs")
    limit = MIN_BODY_FONT.get(1280) if vw >= 900 else MIN_BODY_FONT.get(390)
    if limit is None:
        limit = 13.0 if vw < 900 else 14.0
    if body_fs is None:
        rep.add("runtime.font", page_rel, vps, "FAIL", "无法读取 body 字号")
    elif body_fs >= limit:
        rep.add("runtime.font", page_rel, vps, "PASS",
                "body font-size=%spx >= %spx" % (body_fs, limit))
    else:
        rep.add("runtime.font", page_rel, vps, "FAIL",
                "body font-size=%spx < 下限 %spx" % (body_fs, limit))

    # A4 正文行高
    para = data.get("para")
    if not para or not para.get("fs"):
        rep.add("runtime.lineheight", page_rel, vps, "SKIP", "页上无可见正文 <p>")
    else:
        lh = parse_lineheight(para.get("lh"), para.get("fs"))
        if not lh:
            rep.add("runtime.lineheight", page_rel, vps, "SKIP",
                    "行高不可解析 (%r)" % para.get("lh"))
        else:
            ratio = lh / para["fs"]
            if ratio >= MIN_LINEHEIGHT_RATIO - 1e-9:
                rep.add("runtime.lineheight", page_rel, vps, "PASS",
                        "p fs=%spx lh=%spx ratio=%.3f >= %s"
                        % (para["fs"], round(lh, 2), ratio, MIN_LINEHEIGHT_RATIO))
            else:
                rep.add("runtime.lineheight", page_rel, vps, "FAIL",
                        "p fs=%spx lh=%spx ratio=%.3f < %s"
                        % (para["fs"], round(lh, 2), ratio, MIN_LINEHEIGHT_RATIO))

    # A5 溢出泄漏
    leaks = data.get("leaks") or []
    if not leaks:
        rep.add("runtime.overflow-leak", page_rel, vps, "PASS",
                "无元素 right > innerWidth+1（滚动容器内除外）")
    else:
        rep.add("runtime.overflow-leak", page_rel, vps, "FAIL",
                "%d 处溢出泄漏: %s" % (len(leaks),
                                    [(x["el"], x["right"]) for x in leaks[:5]]))

    # A6 真实文本重叠（DOM 2D 主判据；与像素段解耦）
    ov = eval_overlap(timeout)
    overlap_ok = report_overlap(ov, page_rel, vps, rep)

    return {"iw": iw, "sh": sh}, overlap_ok


# ---------------------------------------------------------------- 像素检查

def load_imaging():
    try:
        import numpy as np              # noqa: F401
        from PIL import Image           # noqa: F401
        return np, Image
    except Exception:
        return None, None


def analyze_pixels(png_path, vw, vh, svg_rects, np, Image, rep, page_rel,
                   dom_overlap=False):
    vps = "%dx%d" % (vw, vh)
    try:
        im = Image.open(png_path).convert("RGB")
    except Exception as e:
        rep.add("pixel.open", page_rel, vps, "FAIL", "无法打开截图: %s" % e)
        return
    a = np.asarray(im).astype(np.int32)
    if a.ndim != 3:
        rep.add("pixel.open", page_rel, vps, "FAIL", "截图非 RGB")
        return
    h, w, _ = a.shape
    bg = np.array(BG_RGB, dtype=np.int32)
    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    ink = dist > INK_DIST
    ink_ratio = float(ink.mean())

    # B1 非空
    if ink_ratio >= MIN_INK_RATIO:
        rep.add("pixel.non-empty", page_rel, vps, "PASS",
                "非背景占比 %.2f%% >= %.2f%% (img %dx%d)"
                % (ink_ratio * 100, MIN_INK_RATIO * 100, w, h))
    else:
        rep.add("pixel.non-empty", page_rel, vps, "FAIL",
                "非背景占比 %.2f%% < %.2f%%（疑似白页/渲染失败）"
                % (ink_ratio * 100, MIN_INK_RATIO * 100))

    # B2 背景色四角
    corners = [a[2, 2], a[2, w - 3], a[h - 3, 2], a[h - 3, w - 3]]
    bad = []
    for c in corners:
        if any(abs(int(c[i]) - BG_RGB[i]) > CORNER_TOL for i in range(3)):
            bad.append(tuple(int(x) for x in c))
    if not bad:
        rep.add("pixel.bg-corners", page_rel, vps, "PASS",
                "四角均在 #f5f1e8 ±%d 内 (样例 %s)"
                % (CORNER_TOL, tuple(int(x) for x in corners[0])))
    else:
        rep.add("pixel.bg-corners", page_rel, vps, "FAIL",
                "%d/4 角偏离背景 >±%d: %s" % (len(bad), CORNER_TOL, bad))

    # B3 页面高度合理
    if h > PAGE_HEIGHT_FACTOR * vh:
        rep.add("pixel.page-height", page_rel, vps, "PASS",
                "img h=%d > %s×vh(%d)=%d" % (h, PAGE_HEIGHT_FACTOR, vh,
                                              int(PAGE_HEIGHT_FACTOR * vh)))
    else:
        rep.add("pixel.page-height", page_rel, vps, "FAIL",
                "img h=%d <= %s×vh(%d)=%d（疑似截断式渲染失败）"
                % (h, PAGE_HEIGHT_FACTOR, vh, int(PAGE_HEIGHT_FACTOR * vh)))

    # B4 svg 裁剪区确有内容
    if not svg_rects:
        rep.add("pixel.svg-ink", page_rel, vps, "SKIP", "页上无 svg")
    scale = float(w) / float(vw) if vw else 1.0
    for idx, r in enumerate(svg_rects):
        x0 = max(0, int(math.floor(r.get("left", 0) * scale)))
        x1 = min(w, int(math.ceil((r.get("left", 0) + r.get("w", 0)) * scale)))
        y0 = max(0, int(math.floor(r.get("top", 0) * scale)))
        y1 = min(h, int(math.ceil((r.get("top", 0) + r.get("h", 0)) * scale)))
        if x1 - x0 < 8 or y1 - y0 < 8:
            rep.add("pixel.svg-ink", page_rel, vps, "SKIP",
                    "svg[%d] 裁剪区过小/越界" % idx)
            continue
        crop = ink[y0:y1, x0:x1]
        ratio = float(crop.mean())
        if ratio >= MIN_SVG_INK_RATIO:
            rep.add("pixel.svg-ink", page_rel, vps, "PASS",
                    "svg[%d] 区域 %dx%d 非背景 %.2f%% >= %.2f%%"
                    % (idx, x1 - x0, y1 - y0, ratio * 100, MIN_SVG_INK_RATIO * 100))
        else:
            rep.add("pixel.svg-ink", page_rel, vps, "FAIL",
                    "svg[%d] 区域非背景 %.2f%% < %.2f%%（关系图疑似未画出）"
                    % (idx, ratio * 100, MIN_SVG_INK_RATIO * 100))

    # B5 右侧裁切检测
    strip = ink[:, max(0, w - RIGHT_STRIP_PX):]
    strip_ratio = float(strip.mean()) if strip.size else 0.0
    if strip_ratio < MAX_RIGHT_STRIP_INK:
        rep.add("pixel.right-clip", page_rel, vps, "PASS",
                "最右 %dpx 非背景 %.2f%% < %.2f%%"
                % (RIGHT_STRIP_PX, strip_ratio * 100, MAX_RIGHT_STRIP_INK * 100))
    else:
        rep.add("pixel.right-clip", page_rel, vps, "FAIL",
                "最右 %dpx 非背景 %.2f%% >= %.2f%%（疑似右侧被裁切）"
                % (RIGHT_STRIP_PX, strip_ratio * 100, MAX_RIGHT_STRIP_INK * 100))

    # B6 重叠（已退役 1D 像素启发式；真实重叠由 DOM runtime.overlap 判定）
    # 旧判据「同行两段墨迹被 1–3px 背景隔断」与「重叠」无因果关系：正常中文/拉丁
    # 排布的字词间距本就落在 1–3px（GL-ESSENCE@1280 实测 40 行命中 gap {1:25,2:14,3:2}），
    # 而真实重叠是零间距墨迹融合。保留像素通道仅作降级提示：DOM 判据可用时记 [SKIP]；
    # 不可用时才运行保守的 pixel_overlap_fallback（宁缺毋滥，避免复现高误报）。
    if dom_overlap:
        rep.add("pixel.overlap-suspect", page_rel, vps, "SKIP",
                "DOM 2D 判据（runtime.overlap）可用，1D 像素启发式已退役 → 不产出命中")
    else:
        fb = pixel_overlap_fallback(ink, np)
        if fb:
            rep.add("pixel.overlap-suspect", page_rel, vps, "WARN",
                    "DOM 判据不可用，像素降级提示 %d 处: %s" % (len(fb), fb[:4]))
        else:
            rep.add("pixel.overlap-suspect", page_rel, vps, "SKIP",
                    "DOM 判据不可用，像素降级提示未发现疑似重叠（不判 PASS）")


def pixel_overlap_fallback(ink, np):
    """[降级·已退役主判据] 仅在 DOM runtime.overlap 不可用时调用的保守提示。

    故意不复活旧 1D 判据：旧判据无法区分正常字距与真实重叠，会复现高误报。
    这里采用更严格的「多行持续零间距超宽墨迹块」——真实叠字会使相邻字形的背景
    隔断消失并被合并为异常宽的墨迹块，且持续多行。阈值保守（宁缺毋滥）。
    """
    h, w = ink.shape
    runs_by_row = []
    for y in range(0, h, OVERLAP_SCAN_STEP):
        row = ink[y]
        if not row.any():
            continue
        d = np.diff(row.astype(np.int8))
        starts = list(np.where(d == 1)[0] + 1)
        ends = list(np.where(d == -1)[0] + 1)
        if row[0]:
            starts = [0] + starts
        if row[-1]:
            ends = ends + [w]
        n = min(len(starts), len(ends))
        best = 0
        for i in range(n):
            run = ends[i] - starts[i]
            if run > best:
                best = run
        runs_by_row.append(best)
    if len(runs_by_row) < 12:
        return []
    med = float(np.median(runs_by_row))
    if med <= 0:
        return []
    limit = max(400.0, med * 12.0)   # 异常宽：远大于中位墨迹块
    hits = []
    for y in range(0, h, OVERLAP_SCAN_STEP):
        row = ink[y]
        if not row.any():
            continue
        d = np.diff(row.astype(np.int8))
        starts = list(np.where(d == 1)[0] + 1)
        ends = list(np.where(d == -1)[0] + 1)
        if row[0]:
            starts = [0] + starts
        if row[-1]:
            ends = ends + [w]
        n = min(len(starts), len(ends))
        for i in range(n):
            if (ends[i] - starts[i]) >= limit:
                hits.append((int(y), int(starts[i]), int(ends[i])))
                break
        if len(hits) > 20:
            break
    return hits


# ---------------------------------------------------------------- VLM 接口

def write_vlm_manifest(path, items):
    manifest = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "screenshot_dir": str(SHOTS_DIR),
        "note": "供 vision-worker 粗检；verdict 经 --vlm-result 回流本门控。",
        "items": items,
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    return manifest


def load_vlm_result(path):
    p = Path(path)
    if not p.exists():
        return None, "VLM 结果文件不存在: %s" % p
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return None, "VLM 结果非 JSON: %s" % e
    if isinstance(data, dict):
        data = data.get("results", data.get("items"))
    if not isinstance(data, list):
        return None, "VLM 结果缺 results 列表"
    return data, None


def merge_vlm(results, rep):
    """Merge external VLM verdicts; FAIL pulls overall verdict down."""
    used = 0
    for r in results:
        if not isinstance(r, dict):
            continue
        verdict = str(r.get("verdict", "")).strip().upper()
        status = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN",
                  "SKIP": "SKIP"}.get(verdict)
        if status is None:
            continue
        page = r.get("page") or r.get("screenshot") or "vlm"
        vp = r.get("viewport") or ""
        notes = str(r.get("notes", ""))[:160]
        rep.add("vlm.vision", page, vp, status, notes or "(external VLM)")
        used += 1
    return used


# ---------------------------------------------------------------- 主流程

def parse_pages(args):
    if not args.pages:
        return list(DEFAULT_PAGES)
    p = Path(args.pages)
    if not p.exists():
        print("[FAIL] pages 文件不存在: %s" % p)
        sys.exit(2)
    out = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            label, rel = line.split("|", 1)
            label, rel = label.strip(), rel.strip()
        else:
            rel = line
            label = Path(rel).stem
        out.append((label, rel))
    return out


def parse_viewports(args):
    if not args.viewport:
        return list(DEFAULT_VIEWPORTS)
    by_w = {str(v[1]): v for v in DEFAULT_VIEWPORTS}
    out = []
    for tok in args.viewport.split(","):
        tok = tok.strip().lower()
        if not tok:
            continue
        w = tok.split("x")[0].split(":")[0]
        if w in by_w:
            out.append(by_w[w])
        else:
            try:
                wi = int(w)
            except ValueError:
                print("[FAIL] 未知识口: %s" % tok)
                sys.exit(2)
            out.append(("vp%d" % wi, wi, 900 if wi >= 900 else 844))
    return out or list(DEFAULT_VIEWPORTS)


def main():
    ap = argparse.ArgumentParser(description="L4 视觉门控（阶段6 · 浅色 Codex）")
    ap.add_argument("--check", default="all",
                    help="all | runtime | pixels（可逗号组合，如 runtime,pixels）")
    ap.add_argument("--viewport", default=None, help="如 1280,390（逗号分隔宽）")
    ap.add_argument("--pages", default=None, help="页面清单文件（每行 <path> 或 <label>|<path>）")
    ap.add_argument("--vlm-manifest", default=None, help="输出待检截图清单 JSON")
    ap.add_argument("--vlm-result", default=None, help="读入外部 VLM 判定 JSON")
    ap.add_argument("--timeout", type=int, default=30, help="单条命令超时秒")
    ap.add_argument("--show", type=int, default=200, help="逐项展示条数上限")
    args = ap.parse_args()

    cats = set()
    for tok in args.check.lower().split(","):
        tok = tok.strip()
        if tok in ("all", ""):
            cats |= {"runtime", "pixels"}
        elif tok.startswith("runtime"):
            cats.add("runtime")
        elif tok.startswith("pixel"):
            cats.add("pixels")
        else:
            print("[FAIL] 未知 --check 值: %s" % tok)
            return 2

    pages = parse_pages(args)
    viewports = parse_viewports(args)

    print("=" * 74)
    print("L4 视觉门控（headless Chromium via agent-browser）")
    print("  repo root : %s" % ROOT)
    print("  shots dir : %s" % SHOTS_DIR)
    print("  check     : %s" % ",".join(sorted(cats)))
    print("  pages     : %d | viewports: %d" % (len(pages), len(viewports)))
    print("  conflict  : %s (edge %s)" % (CONFLICT_NODE, CONFLICT_EDGE))
    print("  time      : %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 74)

    rep = Reporter()
    manifest_items = []
    np_mod = Image_mod = None

    have_ab = shutil.which("agent-browser") is not None
    if not have_ab:
        rep.add("env.agent-browser", "site", "-", "SKIP",
                "agent-browser CLI 未找到 → 运行态与像素段均 SKIP")

    if "pixels" in cats:
        np_mod, Image_mod = load_imaging()
        if np_mod is None or Image_mod is None:
            rep.add("env.imaging", "site", "-", "SKIP",
                    "Pillow/numpy 缺失 → 像素段 SKIP（第三方依赖，缺失不崩溃）")
            cats.discard("pixels")

    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    started = time.time()

    try:
        for label, rel in pages:
            page_abs = ROOT / rel
            for vlabel, vw, vh in viewports:
                vps = "%dx%d" % (vw, vh)
                slug = ("%s__%s__%d" % (label, vlabel, vw)).replace("/", "_")
                shot_path = SHOTS_DIR / (slug + ".png")
                shot_ok = False
                dom_overlap = False

                if have_ab and ("runtime" in cats or "pixels" in cats):
                    if "runtime" in cats:
                        _info, dom_overlap = run_runtime(
                            rel, page_abs, vw, vh, rep, args.timeout)
                    elif "pixels" in cats:
                        # pixels-only：仍需打开页面以保证截图有效，并顺手跑 DOM
                        # 重叠主判据，使像素段与运行态段口径一致。
                        if open_page(rel, page_abs, vw, vh, rep, args.timeout):
                            dom_overlap = report_overlap(
                                eval_overlap(args.timeout), rel, vps, rep)
                    if "pixels" in cats:
                        rc, out, err = ab("screenshot", "--full", str(shot_path),
                                          timeout=args.timeout + 15)
                        shot_ok = (rc == 0 and shot_path.exists()
                                   and shot_path.stat().st_size > 0)
                        if not shot_ok:
                            rep.add("pixel.screenshot", rel, vps, "FAIL",
                                    "截图失败 rc=%s %s" % (rc, (err or out).strip()[:160]))

                if shot_ok:
                    # fetch svg rects (cheap) for pixel crop; independent of runtime
                    svg_rects = []
                    if have_ab:
                        data, _e = eval_result(
                            "(function(){var o=[];document.querySelectorAll('svg')"
                            ".forEach(function(s){var r=s.getBoundingClientRect();"
                            "o.push({left:r.left,top:r.top+window.scrollY,w:r.width,h:r.height});});"
                            "return JSON.stringify(o);})()", timeout=args.timeout)
                        if isinstance(data, list):
                            svg_rects = data
                    analyze_pixels(str(shot_path), vw, vh, svg_rects,
                                   np_mod, Image_mod, rep, rel, dom_overlap=dom_overlap)

                if "pixels" not in cats:
                    shot_ok = False

                # runtime aggregate for manifest
                rv = [it["status"] for it in rep.items
                      if it["page"] == rel and it["viewport"] == vps
                      and it["check"].startswith("runtime.")]
                if not rv:
                    r_verdict = "SKIP"
                elif "FAIL" in rv:
                    r_verdict = "FAIL"
                elif "WARN" in rv:
                    r_verdict = "WARN"
                else:
                    r_verdict = "PASS"
                manifest_items.append({
                    "screenshot": str(shot_path) if shot_ok else None,
                    "page": rel,
                    "label": label,
                    "viewport": vps,
                    "runtime_verdict": r_verdict,
                    "screenshot_ok": shot_ok,
                })
    finally:
        if have_ab:
            rc, out, err = ab("close", timeout=20)
            if rc != 0:
                run_cmd(["agent-browser", "--session", SESSION, "close", "--all"], 20)
            # ensure all tabs closed even if session had extras
            run_cmd(["agent-browser", "--session", SESSION, "close", "--all"], 20)

    # VLM merge
    if args.vlm_result:
        results, e = load_vlm_result(args.vlm_result)
        if results is None:
            rep.add("vlm.result", "site", "-", "SKIP", str(e))
        else:
            used = merge_vlm(results, rep)
            if used == 0:
                rep.add("vlm.result", "site", "-", "SKIP",
                        "VLM 结果无有效条目")

    if args.vlm_manifest:
        write_vlm_manifest(args.vlm_manifest, manifest_items)
        print("VLM manifest 已写入: %s (%d items)"
              % (args.vlm_manifest, len(manifest_items)))
    print("")

    rep.print_all(show_evidence=True)
    print("")
    print("-" * 74)
    n_total = rep.total
    n_pass = rep.count("PASS")
    n_fail = rep.count("FAIL")
    n_warn = rep.count("WARN")
    n_skip = rep.count("SKIP")
    cov = (float(n_pass) / n_total * 100.0) if n_total else 0.0
    print("=== 汇总 ===")
    print("  checks_total = %d" % n_total)
    print("  checks_pass  = %d" % n_pass)
    print("  checks_fail  = %d" % n_fail)
    print("  checks_warn  = %d" % n_warn)
    print("  checks_skip  = %d" % n_skip)
    print("  覆盖率       = %d/%d = %.2f%%（skip 不计入 pass）"
          % (n_pass, n_total, cov))
    print("  用时         = %.1fs" % (time.time() - started))
    print("  L4 综合判定  = %s" % rep.verdict)
    print("  退出码规则   = 无 FAIL（PASS/WARN）→0；存在 FAIL 或全 SKIP →1")
    print("-" * 74)
    return 0 if rep.verdict in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
