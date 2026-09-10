#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成交互 DAG 总览：{out_interactive}/index.html（cytoscape + dagre）。

通用化要点：
  - DATA 内联注入 nodes（含 layer/domain/cross_cutting/case，缺失自动省略）
  - 组级视图 → 点击下钻组内 DAG；桥接高亮模式仅在存在 bridge 节点时展示有效
  - 组配色由 group.kind 派生，不硬编码组 ID
  - vendor 来源优先级：--vendor-src > 数据同级 {interactive}/vendor > 输出既有 vendor
"""
import argparse
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (build_graph, esc, EDGE_STYLE, STAGE_STYLE, KIND_STYLE,
                        LAYER_STYLE, add_common_args, config_from_args)

GROUP_COLOR_BY_KIND = {
    "layer": "#4f8cff", "domain": "#5ad0d0", "source": "#4f8cff",
    "bridge": "#2fb98a", "crosscut": "#b48ae0", "case": "#e05563", "tool": "#e0c35e",
}
STAGE_COLOR_MAP = {"basic": "#4f8cff", "intermediate": "#2fb98a", "advanced": "#e8933b"}


def build_data(g):
    nodes = []
    for n in g.nodes:
        d = {"id": n["id"], "name": n["name"], "type": n["type"], "group": n.get("group") or "",
             "stage": n.get("stage"), "brief": n.get("definition", "")}
        for k in ("src", "layer", "domain"):
            if n.get(k):
                d[k] = n[k]
        if n.get("cross_cutting"):
            d["cc"] = n["cross_cutting"]
        if n.get("case"):
            d["case"] = n["case"]
        if n.get("status"):
            d["status"] = n["status"]
        nodes.append(d)

    edges = [{"from": e["from"], "to": e["to"], "type": e["type"], "label": e.get("label", "")}
             for e in g.edges if e["from"] in g.by_id and e["to"] in g.by_id]

    groups = []
    for gp in g.groups:
        nids = [x for x in gp["node_ids"] if x in g.by_id]
        stages = sorted({g.by_id[x]["stage"] for x in nids},
                        key=lambda s: (["basic", "intermediate", "advanced"].index(s)
                                       if s in ["basic", "intermediate", "advanced"] else 99))
        groups.append({"id": gp["id"], "name": gp["name"], "domain": gp.get("domain", ""),
                       "kind": gp.get("kind", "source"), "stage_range": stages, "node_ids": nids})

    group_edges = []
    seen = set()
    for e in g.edges:
        if e["type"] != "prerequisite":
            continue
        gf = g.node_to_group.get(e["from"])
        gt = g.node_to_group.get(e["to"])
        if not gf or not gt or gf == gt:
            continue
        key = gf + "|" + gt
        if key in seen:
            continue
        seen.add(key)
        group_edges.append({"source": gf, "target": gt, "viaFrom": e["from"],
                            "viaTo": e["to"], "type": e["type"]})

    group_color = {}
    for gp in groups:
        group_color[gp["id"]] = GROUP_COLOR_BY_KIND.get(gp["kind"], "#243040")

    return {
        "meta": {
            "title": g.cfg["title"], "subtitle": g.cfg.get("subtitle", ""),
            "total_groups": len(groups), "total_nodes": len(nodes), "total_edges": len(edges),
            "stages": ["basic", "intermediate", "advanced"],
            "edge_types": sorted({e["type"] for e in g.edges}),
            "dag_acyclic": True,
            "has_bridge": any(n.get("type") == "bridge" or n.get("src") == "bridge" for n in g.nodes),
        },
        "groups": groups, "nodes": nodes, "edges": edges, "groupEdges": group_edges,
        "groupColor": group_color, "stageColor": STAGE_COLOR_MAP,
        "edgeColor": {k: v["brd"] for k, v in EDGE_STYLE.items()},
    }


CSS = """
  :root { --bg:#0f1117; --panel:#161a22; --border:#2a2f3a; --text:#e6e8ee; --dim:#9aa3b2; --accent:#4f8cff; --warn:#e0c35e; --danger:#e05563; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,sans-serif; height:100vh; overflow:hidden; }
  header { position:fixed; top:0; left:0; right:0; z-index:10; background:var(--panel); border-bottom:1px solid var(--border); padding:8px 16px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  header h1 { font-size:15px; font-weight:600; white-space:nowrap; }
  header a { color:var(--accent); text-decoration:none; font-size:13px; }
  header a:hover { text-decoration:underline; }
  .badge { background:#20324f; color:#7fb0ff; padding:2px 10px; border-radius:20px; font-size:12px; white-space:nowrap; }
  .controls { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
  .btn { background:#20324f; color:#7fb0ff; border:1px solid #2a3a55; border-radius:20px; padding:4px 14px; font-size:12px; cursor:pointer; white-space:nowrap; }
  .btn:hover { background:#2a3a55; }
  .btn.on { background:#0f2b1f; color:#6fd3ae; border-color:#2fb98a; }
  #side { position:fixed; right:0; top:52px; bottom:0; width:300px; background:var(--panel); border-left:1px solid var(--border); padding:14px; overflow:auto; z-index:9; }
  #side h2 { font-size:13px; margin-bottom:8px; color:var(--dim); }
  #side .legend { font-size:12px; color:var(--dim); line-height:1.9; }
  #side .legend b { color:var(--text); }
  #side .legend .sw { display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:6px; vertical-align:-1px; }
  #zoominfo { position:fixed; bottom:14px; left:18px; background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:7px 12px; font-size:12px; color:var(--dim); z-index:9; }
  #zoominfo b { color:var(--text); }
  #crumb { position:fixed; top:52px; left:18px; background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:6px 12px; font-size:12px; color:var(--dim); z-index:9; display:none; align-items:center; gap:8px; }
  #crumb b { color:var(--accent); }
  #graph { position:fixed; top:52px; left:0; right:0; bottom:0; }
  #glegend { margin-top:6px; }
  #glegend .row { display:flex; align-items:center; gap:8px; font-size:12px; color:var(--dim); margin:3px 0; cursor:pointer; }
  #glegend .row:hover { color:var(--text); }
  #glegend .row .sw { width:14px; height:14px; border-radius:3px; flex:0 0 auto; }
  @media (max-width:768px){ #side { width:220px; } header { padding:6px 10px; gap:8px; } header h1 { font-size:13px; } }
"""

JS = r"""
(function(){
  'use strict';
  const DATA = __DATA__;
  const EDGE_COLOR = DATA.edgeColor;
  const STAGE_COLOR = DATA.stageColor;
  const EDGE_LABEL = __EDGE_LABELS__;
  const nodeById = {}; DATA.nodes.forEach(n => nodeById[n.id] = n);
  const groupById = {}; DATA.groups.forEach(g => groupById[g.id] = g);
  const nodeToGroup = {}; DATA.groups.forEach(g => g.node_ids.forEach(nid => nodeToGroup[nid] = g.id));
  const groupNodeIndex = {}; DATA.groups.forEach(g => g.node_ids.forEach((nid,i) => { groupNodeIndex[nid] = i; }));
  let currentGroup = null, bridgeMode = false;

  const $ = id => document.getElementById(id);
  const crumb = $('crumb');
  function isBridge(nid){ const n = nodeById[nid]; return n && (n.type === 'bridge' || n.src === 'bridge'); }

  function buildGroupNodes(){
    const nodes = DATA.groups.map(g => ({ data:{ id:'grp-'+g.id, label:g.name, kind:'group', group:g.id, gname:g.name, domain:g.domain, gkind:g.kind, totalCount:g.node_ids.length } }));
    const edges = []; const seen = new Set();
    DATA.groupEdges.forEach(ge => {
      const k = ge.source+'|'+ge.target;
      if (seen.has(k)) return; seen.add(k);
      edges.push({ data:{ id:'grp-'+ge.source+'->grp-'+ge.target, source:'grp-'+ge.source, target:'grp-'+ge.target, kind:'group', type:ge.type } });
    });
    return { nodes, edges };
  }

  function buildGroupDrill(gid){
    const g = groupById[gid]; const members = g.node_ids; const memberSet = new Set(members);
    const relatedIds = new Set(members); const edges = [];
    DATA.edges.forEach(e => {
      if (bridgeMode && !(isBridge(e.from) || isBridge(e.to))) return;
      const s=e.from, t=e.to, sIn=memberSet.has(s), tIn=memberSet.has(t);
      if (sIn && tIn){ edges.push({ data:{ id:s+'->'+t, source:s, target:t, type:e.type, label:e.label } }); }
      else if (sIn || tIn){ const other = sIn?t:s; if (nodeById[other] && !memberSet.has(other)){ relatedIds.add(other); edges.push({ data:{ id:s+'->'+t, source:s, target:t, type:e.type, label:e.label } }); } }
    });
    const nodes = [];
    relatedIds.forEach(id => { const n=nodeById[id]; if(!n) return; const isMember=memberSet.has(id);
      nodes.push({ data:{ id, label:n.name, kind:'node', group:n.group, gname: groupById[n.group]?groupById[n.group].name:'', stage:n.stage, src:n.src||'', layer:n.layer||'', brief:n.brief||'', member:isMember, mode:isMember?'member':'stub' } }); });
    nodes.sort((a,b)=>{ const am=a.data.member?0:1, bm=b.data.member?0:1; if(am!==bm) return am-bm;
      if(a.data.member) return (groupNodeIndex[a.data.id]||0)-(groupNodeIndex[b.data.id]||0); return a.data.id<b.data.id?-1:1; });
    return { nodes, edges };
  }

  function buildBridgeView(){
    const bridgeIds = DATA.nodes.filter(n => isBridge(n.id)).map(n => n.id);
    const idSet = new Set(bridgeIds);
    const nodes = bridgeIds.map(id => { const n=nodeById[id]; return { data:{ id, label:n.name, kind:'node', group:n.group, gname:groupById[n.group]?groupById[n.group].name:'', stage:n.stage, src:n.src||'', brief:n.brief||'', member:true, mode:'member' } }; });
    const edges = [];
    DATA.edges.forEach(e => { if(idSet.has(e.from) && idSet.has(e.to)) edges.push({ data:{ id:e.from+'->'+e.to, source:e.from, target:e.to, type:e.type, label:e.label } }); });
    return { nodes, edges };
  }

  function render(doFit=true){
    let els, mode;
    if (bridgeMode){ els = buildBridgeView(); mode='桥接主题'; }
    else if (currentGroup === null){ els = buildGroupNodes(); mode='组级'; }
    else { els = buildGroupDrill(currentGroup); mode = currentGroup+' · '+(groupById[currentGroup]?groupById[currentGroup].name:''); }
    cy.elements().remove(); cy.add(els.nodes); cy.add(els.edges);
    cy.nodes().forEach(n => { const d=n.data(); let op=1; if(bridgeMode){ if(d.kind==='node' && !isBridge(d.id)) op=0.08; if(d.kind==='group') op=0.15; } n.style('opacity', op); });
    $('zcount').textContent = cy.nodes().length;
    $('zmode').textContent = mode;
    cy.layout({ name:'dagre', rankDir:'LR', nodeSep:40, rankSep:70, padding:40 }).run();
    if (doFit) cy.fit(undefined, 50);
    updateCrumb();
  }

  function goBack(){ if (currentGroup !== null){ currentGroup=null; render(); } }
  function toggleBridge(){ bridgeMode=!bridgeMode; currentGroup=null; $('bridgebtn').classList.toggle('on', bridgeMode); render(); }

  const cy = cytoscape({
    container: document.getElementById('graph'), elements: [],
    style: [
      { selector:'node', style:{ label:'data(label)', 'text-valign':'center','text-halign':'center', color:'#fff', 'font-size':9, 'text-wrap':'wrap', 'text-max-width':90 } },
      { selector:'node[kind="group"]', style:{ 'background-color': function(ele){ return DATA.groupColor[ele.data('group')] || '#243040'; }, 'border-width':3,'border-color':'rgba(255,255,255,0.5)','width':130,'height':46,'font-size':12,'text-wrap':'wrap','text-max-width':116 } },
      { selector:'node[kind="node"]', style:{ 'background-color': function(ele){ return DATA.groupColor[ele.data('group')] || '#2b3550'; }, 'border-width':1,'border-color':'rgba(255,255,255,0.35)','width':58,'height':30, shape:'round-rectangle' } },
      { selector:'node[kind="node"][mode="stub"]', style:{ 'background-color':'#2a2e38','border-color':'#555a66','width':52,'height':26, opacity:0.55, 'font-size':8 } },
      { selector:'edge', style:{ 'curve-style':'bezier','target-arrow-shape':'triangle','arrow-scale':0.7, 'line-color': function(ele){ return EDGE_COLOR[ele.data('type')] || '#4a5265'; }, 'target-arrow-color': function(ele){ return EDGE_COLOR[ele.data('type')] || '#4a5265'; }, 'width':1.3 } },
      { selector:'edge[type="prerequisite"]', style:{ 'width':2.0 } },
      { selector:'edge[type="variant"]', style:{ 'line-style':'dashed' } },
      { selector:'edge[type="cooccurrence"]', style:{ 'line-style':'dotted' } }
    ],
    layout: { name:'dagre', rankDir:'LR', nodeSep:40, rankSep:70, padding:40 },
    wheelSensitivity:0.3, minZoom:0.05, maxZoom:5
  });
  window.__cy = cy;

  cy.on('tap', 'node', (evt) => { const d=evt.target.data();
    if (currentGroup===null){ if(d.kind==='group'){ currentGroup=d.group; render(); } }
    else { if(d.kind==='node'){ window.location.href = '../__NODEDIR__/'+d.id+'.html'; } } });

  function handleHash(){ const h=location.hash.replace(/^#/,''); if(!h) return;
    if (groupById[h]){ currentGroup=h; bridgeMode=false; $('bridgebtn').classList.remove('on'); render(); }
    else if (nodeById[h]){ const gp=nodeToGroup[h]; if(gp){ currentGroup=gp; bridgeMode=false; render(); } } }
  window.addEventListener('hashchange', handleHash);

  function updateCrumb(){ if (currentGroup!==null && !bridgeMode){ const gp=groupById[currentGroup];
      crumb.style.display='inline-flex'; $('backbtn').style.display='inline-block';
      crumb.innerHTML='<b>'+currentGroup+'</b> '+escapeHtml(gp?gp.name:'')+' <span style="color:var(--dim)">· '+(gp?gp.node_ids.length:0)+' 节点</span>'; }
    else { crumb.style.display='none'; $('backbtn').style.display='none'; } }
  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  function buildLegend(){ const lg=$('legend'); let html='';
    html += '<b>组节点</b>（'+DATA.groups.length+' 组，彩色，点击下钻）<br>';
    html += '<b>知识节点</b>（'+DATA.nodes.length+' 个，点击跳转节点页）<br><b>边类型</b>：<br>';
    Object.keys(EDGE_COLOR).forEach(t => { html += '<span class="sw" style="background:'+EDGE_COLOR[t]+'"></span>'+(EDGE_LABEL[t]||t)+'<br>'; });
    if (DATA.meta.has_bridge) html += '<b>桥接模式</b>：仅显示桥接主题及其连接边';
    lg.innerHTML = html; }

  const gl=$('glegend');
  DATA.groups.forEach(g => { const d=document.createElement('div'); d.className='row';
    const sw=document.createElement('span'); sw.className='sw'; sw.style.background=DATA.groupColor[g.id]||'#243040';
    const txt=document.createElement('span'); txt.textContent=g.name+' ('+g.id+')';
    d.appendChild(sw); d.appendChild(txt);
    d.addEventListener('click', () => { currentGroup=g.id; bridgeMode=false; $('bridgebtn').classList.remove('on'); render(); });
    gl.appendChild(d); });

  $('bridgebtn').addEventListener('click', toggleBridge);
  $('backbtn').addEventListener('click', goBack);
  buildLegend(); render(); handleHash();
})();
"""


def ensure_vendor(cfg, dest_dir):
    vendor_dir = os.path.join(dest_dir, "vendor")
    os.makedirs(vendor_dir, exist_ok=True)
    need = ["cytoscape.min.js", "cytoscape-dagre.min.js"]
    if all(os.path.exists(os.path.join(vendor_dir, f)) for f in need):
        return True
    candidates = []
    if cfg.get("vendor_src"):
        candidates.append(cfg["vendor_src"])
    if cfg.get("data_dir"):
        candidates.append(os.path.normpath(os.path.join(cfg["data_dir"], os.pardir,
                                                        cfg["out_dirs"]["interactive"], "vendor")))
    for cand in candidates:
        if all(os.path.exists(os.path.join(cand, f)) for f in need):
            for f in need:
                shutil.copy2(os.path.join(cand, f), os.path.join(vendor_dir, f))
            return True
    sys.stderr.write("[warn] 未找到 vendor JS（cytoscape），交互图将缺依赖；"
                     "可经 --vendor-src 指定\n")
    return False


def run(cfg):
    out = cfg["out_paths"]["interactive"]
    os.makedirs(out, exist_ok=True)
    g = build_graph(cfg)
    data = build_data(g)
    js = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    edge_labels = {k: v["label"] for k, v in EDGE_STYLE.items()}
    js = js.replace("__EDGE_LABELS__", json.dumps(edge_labels, ensure_ascii=False))
    js = js.replace("__NODEDIR__", cfg["out_dirs"]["nodes"])
    ensure_vendor(cfg, out)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · 交互式 DAG 总览</title>
<style>{css}</style>
</head>
<body>
<header>
  <h1>{title} <span class="badge">交互 DAG</span></h1>
  <a href="../{root}">← 根入口</a>
  <a href="../{groups}/index.html">组目录</a>
  <span id="crumb"></span>
  <button id="backbtn" class="btn" style="display:none;">← 返回组级</button>
  <div class="controls"><button id="bridgebtn" class="btn">桥接高亮</button></div>
</header>
<div id="graph"></div>
<div id="side">
  <h2>图例</h2><div class="legend" id="legend"></div>
  <h2 style="margin-top:12px;">组配色</h2><div id="glegend"></div>
</div>
<div id="zoominfo">模式 <b id="zmode">组级</b> · 节点 <b id="zcount">0</b></div>
<script src="vendor/cytoscape.min.js"></script>
<script src="vendor/cytoscape-dagre.min.js"></script>
<script>{js}</script>
</body>
</html>
""".format(title=esc(cfg["title"]), css=CSS, js=js,
           root=esc(cfg["root_index"]), groups=esc(cfg["out_dirs"]["groups"]))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return {"kind": "interactive", "written": 1, "nodes": len(data["nodes"]),
            "edges": len(data["edges"]), "groups": len(data["groups"]), "dir": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成交互 DAG 总览")
    add_common_args(ap)
    args = ap.parse_args(argv)
    res = run(config_from_args(args))
    print("interactive written: nodes=%d edges=%d groups=%d -> %s"
          % (res["nodes"], res["edges"], res["groups"], res["dir"]))


if __name__ == "__main__":
    main()
