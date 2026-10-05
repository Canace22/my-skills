# 腾讯混元 3D：网页与 API 路由

以下能力依据 2026-09-17 可见的腾讯官方页面与文档整理，产品入口、免费额度、模型版本和接口参数可能变化。实际执行前核对当前页面；已有任务优先续跑，不因文档更新重新消耗额度。

- [混元 3D 网页创作引擎](https://3d.hunyuan.tencent.com/)
- [腾讯发布的创作引擎能力说明](https://www.tencent.com/zh-cn/tencent-announces-global-launch-of-hunyuan-3d-engine-to-empower-creators-with-advanced-creation-tools/)
- [腾讯云混元生 3D 产品页](https://cloud.tencent.com/product/ai3d)
- [腾讯云 API 概览](https://cloud.tencent.com/document/api/1804/120838)
- [腾讯云快速入门](https://cloud.tencent.com/document/product/1804/120757)

## 先区分两个入口

### 网页创作引擎

适合用户明确指定网页端、希望先使用页面显示的免费额度，或没有腾讯云 API 配置的单次生成。官方公开说明支持文字、图片、草图和最多四张多视图输入，并可输出 OBJ、GLB 等格式；界面实际出现的选项优先于旧说明。

网页流程必须保留：输入图片与提示词、页面显示的任务或作品标识、生成日期、下载的原始文件和预览图。优先下载 GLB 进入 Blender；若只有 OBJ，连同 MTL 和贴图完整保存。网页作品不能只留在线地址。

不要把“混元品牌有此 API”写成“网页端已经提供此按钮”。绑骨、动作、组件化、UV、拓扑或格式转换只有在当前页面真实可见并实际完成时，才算网页流程的一部分。

### 腾讯云 API

适合需要可复现批处理、任务状态记录，或明确要使用云 API 的专业版/极速版、智能拓扑、绑骨蒙皮、文生动作等能力。调用前确认用户已开通服务、当前计费规则和授权范围；不要替用户创建密钥、购买资源包或开启后付费。

使用已有安全配置读取 `TENCENTCLOUD_SECRET_ID` 与 `TENCENTCLOUD_SECRET_KEY`，不要打印、写进项目或发送到网页。国内 API 当前使用 `ai3d.tencentcloudapi.com`，接口版本按当前文档；若官方迁移到 TokenHub 或其他入口，沿用当时的正式文档，不把两套认证方式混用。

常用能力按需求选择，不要整条链全部调用：

- 通用生成：`SubmitHunyuanTo3DProJob` / `QueryHunyuanTo3DProJob`，或明确选用极速版对应接口。
- 自动绑定：`SubmitAutoRiggingJob` / `DescribeAutoRiggingJob`。人形输入保持 A Pose 或 T Pose；动物虽有官方接口描述，也必须按真实物种检查骨骼与权重。
- 文生动作：`SubmitHunyuanTo3DMotionJob` / `DescribeHunyuanTo3DMotionJob`。它输出人物动作 FBX；不要用于证明任意动物动作已经可用。
- 人物头像模板：`SubmitProfileTo3DJob` / `DescribeProfileTo3DJob` 是受模板限制的真人头像路线，不等于任意游戏角色生成。

## 输入与生成策略

- 角色身份已由概念图定稿时，优先图生或多视图，不用一段文字重新发明外形。
- 多视图必须是同一角色、同一服装、同一比例和同一姿态。第一张正面负责身份与面部，侧面负责厚度和前后肢分离，背面负责头发、衣摆和尾巴。
- 文生 3D 使用单主体描述，写清主体、形体、颜色、材质和风格；不要堆入与 3D 结构无关的摄影或画质词。
- 人形需要后续自动绑定时，从输入阶段就保持完整身体、手脚可见、肢体分开和中立 A/T Pose。宽大衣摆、披风、长发或武器贴身会增加绑定失败概率。
- 优先选择 GLB 进入游戏资产流程。是否启用 PBR、面数、四边面/三角面、白模或纹理生成，按目标平台和后续 Blender 工作决定，不照搬高规格。

## 任务记录与恢复

推荐按版本保存：

```text
refs/<character>/source.* + prompt.txt
refs/<character>/front.png + left.png + back.png + right.png  # 需要时
assets/characters/<character>/hunyuan-tasks.json
assets/characters/<character>/hunyuan-source.glb
assets/characters/<character>/<character>.blend
public/models/<character>/<character>.glb                 # 仅 Web 项目示例
output/<character>/                                       # 状态、预览与测试证据
```

记录输入文件 SHA-256、提示词、服务入口、模型/模式、提交参数摘要、JobId、RequestId、状态和实际消耗。不要记录密钥。腾讯云任务 ID 与结果 URL 可能只有 24 小时有效，成功后立即下载到临时文件，校验可读性再移入版本目录。

- 已有 JobId：先查询，不重复提交。
- `WAIT` / `RUN`：适度退避轮询，可并行准备本地接入。
- `DONE`：保存原始产物、预览与完整响应摘要，然后检查几何和材质。
- `FAIL`：记录实际错误；只有输入有实质改进且额度允许时做一次版本化重试。
- 提交超时且没有 JobId：先在控制台或任务列表核对，不靠重复 POST 猜测。
- 下载失败或临时链接过期：优先刷新或重下同一任务产物，不重新生成。

## 混元产物验收

下载后先在 Blender 中检查正侧背轮廓、闭合几何、面部、手指/脚趾、肢体粘连、法线、UV、贴图和材质通道，再决定是否绑定。自动拓扑和 PBR 选项不等于结果已经适合实时游戏；仍要用本 Skill 的 GLB 检查脚本和目标游戏实机验证。

免费额度、赠送积分与商业授权以提交当天页面和条款为准。“免费可生成”不等于可以无限重试，也不自动证明输出满足项目授权要求。
