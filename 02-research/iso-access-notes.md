# ISO 标准可达性实测与获取路线（阶段1 副产物）

- 实测时间：2026-09-10（Build 阶段1）
- 目的：回答"ISO 403 是否因未走代理"的疑问，并确定可用的标准元数据获取路线。

## 实测矩阵

| 目标 | 直连 | 走代理 `172.29.0.1:7890` | 代理 + 浏览器 UA |
|---|---|---|---|
| `https://www.iso.org/standard/50508.html`（42010） | 403 | 403 | 403 |
| `https://www.iso.org/home.html` | 403 | 000（链路抖动） | 403 |
| `https://www.iso-architecture.org/...` | 000 | 000 | — |
| `https://www.sei.cmu.edu/` | — | 200 | — |
| `https://www.computer.org/...` | — | 403 | — |
| `https://iso25000.com/...iso-25010` | — | 200 | — |
| `https://csrc.nist.gov/` | — | 200 | — |
| `https://arxiv.org/abs/2103.01740` | — | 200 | — |
| `https://web.archive.org/web/2023/...iso.org/standard/50508.html` | — | **200（76KB，含真实标题）** | — |

## 结论

1. **`iso.org` 403 = WAF 反爬拦截，与代理无关**（直连/代理/代理+UA 全部 403）。
2. `iso-architecture.org` 为站点级不可达（CONNECT 隧道已建立、TLS 握手 20s 超时），亦非代理问题。
3. **可行获取路线**：`web.archive.org` 快照（首选，可拿到标准页元数据与 scope）+ `iso25000.com` 门户 + SEI 官方页。
4. 标准**正文**涉及版权，仍只作核对依据，不下载入库、不进公开仓库。

## 对阶段2/3 的约束

- 标准类信源获取不再重试 `iso.org`，直接走 Wayback 快照 + iso25000 + SEI。
- 每条标准信源记录：标准号、全名、版本年份、状态、scope 摘要、快照 URL、访问日期。
