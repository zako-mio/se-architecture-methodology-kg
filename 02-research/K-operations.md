# K 证据包：运维（Operations）

- 采集日期：2026-09-10｜角色：可靠性工程师（子Agent）
- 覆盖：SLI/SLO/错误预算、稳定性反模式（断路器/舱壁/超时）、可观测性三支柱、事件响应与无指责复盘、混沌工程、容量与变更管理
- 信源：S2 = Google SRE Book（2017）/ SRE Workbook（2018）/ Nygard《Release It!》2e（2018）/ Fowler bliki / Principles of Chaos（2019）/ Allspaw；S3 = Azure 架构中心、OTel、Datadog、AWS、DORA、MS Well-Architected。共 12 源、19 定义、23 findings，关键定义均 ≥2 独立源交叉验证（Google / Datadog / Microsoft）。

## 一、核心结论

1. **可靠性即风险管理**：100% 不可达且有害（扼杀变更），应选业务可承受的目标。错误预算 = 100% − SLO，把「创新 vs 稳定」之争转为客观发布决策：预算足则发版，耗尽则冻结并加固。
2. **SLI 取值**：推荐「好事件 / 总事件」比值，便于工具化并自然导出错误预算；延迟须看百分位而非均值，并区分成功/失败请求。
3. **告警**：基于 burn rate 的多窗口多燃尽率告警优于单一瞬时错误率，可同时兼顾 precision/recall/detection/reset；分页优先症状（黑盒）。
4. **稳定性反模式**：级联故障本质是正反馈（过载最常见）；用超时、断路器、舱壁隔离、退避+抖动、减载/背压、优雅降级、快速失败对抗。
5. **可观测性**：三支柱 metrics/logs/traces 是通行框架，但 OTel 官方并未使用该措辞（列 Traces/Metrics/Logs/Baggage）；价值在于信号可关联。
6. **事件响应**：尽早宣布并分配 IC/CL/Ops Lead（ICS），维护活文档与显式交接；复盘须无指责（Just Culture），聚焦系统性原因。
7. **混沌工程**：生产受控实验（稳态→假设→注入→证伪），自动化持续、最小化爆炸半径。
8. **容量与变更**：容量走向意图驱动自动规划（N+2 等）；变更是故障首因，靠密封可复现构建 + 分级 rollout + canary 控制，并以 DORA 五指标度量。

## 二、可靠性战术清单

| 战术 | 作用 | 来源 |
|---|---|---|
| Timeout | 限制远程调用等待，防止线程阻塞 | Nygard / Azure |
| Circuit Breaker | 失败超阈值快速失败，给依赖恢复时间 | Fowler / Nygard / Azure |
| Bulkhead/Cell | 资源池分区隔离，故障不扩散 | Azure / Nygard |
| Retry + Backoff + Jitter | 处理瞬时故障并摊平重试风暴（需幂等） | Azure / AWS |
| Shed Load / Back Pressure / Governor | 过载保护，按配额与 criticality 拒绝 | Nygard / SRE Book |
| Graceful Degradation | 极端过载时返回更易计算的降级结果 | SRE Book |
| Fail Fast / Let It Crash | 非瞬态故障快速失败，避免资源浪费 | Nygard |
| Chaos Experiments | 主动验证韧性，最小爆炸半径 | Chaos Principles / Nygard |

## 三、SLI/SLO 定义模板

- **SLI** = `good_events / total_events`（如 成功请求数 / 总请求数；或延迟达标请求数 / 总请求数）。
- **SLO** = `SLI >= target`，例：28 天滚动窗口 99.9% 请求成功；多阈值可写 90%<1ms、99%<10ms、99.9%<100ms。
- **错误预算** = `100% − target`，例：99.9% SLO、28 天 300 万请求 → 3000 个错误。
- **必须声明**：聚合窗口、聚合范围、测量频率、纳入请求、采集位置（server/client）、延迟口径（time to last byte）。
- **目标选择**：勿按当前性能定标；保持简单；避免绝对化；只保留少量 SLO；先松后紧可迭代；内部 SLO 比对外更紧（留安全边际）；勿过度超额（可用计划性下线暴露隐性依赖）。
- **告警**：burn rate 多窗口（如 1h/6h/1d/3d）告警 + 错误预算政策（耗尽后冻结发布/回滚）。
- 参考 SRE Workbook Appendix A「Example SLO Document」与 Appendix B「Example Error Budget Policy」。

## 四、未决问题（gaps）

`sre.google` 依赖代理；Release It! 受版权限制仅核对目录、未提取原句（待本地副本）；无指责复盘缺 Dekker 一手学术源；「三支柱」非 OTel 规范术语、勿作标准定义；PagerDuty 手册待回源；混沌原则停留 2019；DORA 已由四键变五指标（MTTR→Failed Deployment Recovery Time）；量化阈值（burn rate 倍数/canary 比例/N+2）为示例需按服校准；本域 S1 标准（ISO 14764/25010 可靠性）覆盖偏弱，主要靠 S2/S3 支撑。详见 `K-operations.json`。
