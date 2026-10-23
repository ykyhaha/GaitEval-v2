## Reviewer comments 逐项处理

| 编号 | 原意见 | v2 对应处理 | 状态 |
|---|---|---|---|
| R1-1 | ATAXIA/PATHOGAIT 测试参与者太少 | 统一主表给 clips/subjects；ATAXIA S4人/8片段、PATHOGAIT2人，仅描述，保留 L3人限定 | 已处理解释；不能凭写作增加参与者 |
| R1-2 | 发布内容和许可不清楚 | 新仓库、结果生成命令、六数据集来源许可表、明确原视频和缺失资产不打包 | 文档与评分复现完成；完整输入/权重缺失 |
| R1-3 | 同数据集不同表格参考分数不一致 | 正文只用 S 任务匹配主表；L 明细迁补充且协议标清 | 已处理呈现 |
| R1-4 | PATHOGAIT SFT未去 valid-frame feature 重跑 | 明确现有 S 质量特征全排除，但不能当成 L 单变量消融；删除纯运动学优越性解释 | 部分处理；严格 L 消融未执行 |
| R2-1 | 124帧被误写为所有LLM输入 | 定义变长source；解释 L124帧来源、normalized32帧、summary/features聚合 | 已修改 |
| R2-2 | 定性姿态/真实输入/实际输出，成功失败例 | 六数据集各选真实成功和失败输出；overview资源图不冒充对应测试clip | 部分处理；缺少完整 S pose和prompt，无法组成完整对照panel |
| R3-1 | 无新数据，贡献仅协议评测 | 引言/贡献/发布声明明确无新临床录制，贡献是baseline-anchored评测 | 已处理，保持接收版定位 |
| R3-2 | 临床视觉gait文献不足 | 保留已在接收版完善的Related Work与参考文献 | 保留解决 |
| R3-3 / AC | GMFCS参与者泄漏须corrected split并重跑 | 正文S结果255clips/149subjects，来源JSON报告无重叠；旧GMFCS不能支持主结论 | 部分处理；S完整train/test输入和训练日志不在仓库，未独立重做全模型重跑 |

## 最终提交前仍未完成

1. **作者信息**：用户选择保留待核对。PDF作者栏不可直接用于最终上传，必须按OpenReview原顺序补齐姓名/单位/邮箱。
2. **GMFCS corrected split 的独立复核/重跑**：提交的参考JSON报告S无subject overlap，预测日志可验证test集149人；但缺少train/val/test完整实体manifest、输入、adapter及训练日志。不能据此声称本次已经独立解决所有实验性审稿要求。
3. **PATHOGAIT严格单变量feature-SFT消融**：S排除quality feature并非L原设置只去该列的重跑，仍缺少该实验。
4. **完整定性对照panel**：实际输出可查，原始输入和匹配pose不存在；图1是resource示例，不是模型case证据。
5. **图片来源使用条件**：ASD官方归档和CARE-PD官方示例已取；GMFCS仅source demo skeleton，不代表已测患者。ATAXIA源论文图片和PATHOGAIT派生展示的再分发条件须最终确认；来源/修改记录明确保留。不得把可下载等同为统一开源许可。
6. **完整端到端复现**：当前可复现55份预测的point metrics、42共同条件及confusion figures，不能从无输入/权重重做训练。新库明确此范围，绝不宣称全文每个值都已独立重训验证。
7. **正式提交手续**：IEEE PDF eXpress、作者注册、CPS上传、电子版权签署尚未完成；本次仅准备文件，不代签法律文件或支付注册费。

