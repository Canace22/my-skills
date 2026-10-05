# Meshy：任务续跑与资产来源

以下是 2026-09-09 实测接口记录，模型名、参数、价格与返回结构可能变化。首次执行时对照当前官方文档；已有任务按返回数据继续，不因版本变化重新付费提交。

- [Image to 3D](https://docs.meshy.ai/en/api/image-to-3d)
- [Multi-Image to 3D](https://docs.meshy.ai/en/api/multi-image-to-3d)
- [Rigging](https://docs.meshy.ai/en/api/rigging)
- [Balance](https://docs.meshy.ai/en/api/balance)
- [Pricing](https://docs.meshy.ai/en/api/pricing)

## 配置与任务记录

从已有本地环境或项目 `.env` 获取 `MESHY_API_KEY`，不要打印配置全文、密钥或把密钥打包进前端。存在代理时使用已配置的 HTTPS 代理，不假定所有机器需要代理。余额查询是 `GET /openapi/v1/balance`。

推荐按版本存放，名字由当前项目决定：

```text
refs/<character>/source.* + prompt.txt
refs/<character>/front.png + left.png + back.png + right.png  # 需要时使用
assets/characters/<character>/meshy-tasks.json
assets/characters/<character>/meshy-source.glb
assets/characters/<character>/meshy-rigged.glb
assets/characters/<character>/<character>.blend
public/models/<character>/<character>.glb  # 仅 Web 项目示例
output/<character>/                      # 状态响应、渲染与测试证据
```

任务记录保存全部输入图片的组合 SHA-256、请求参数摘要、模型/绑定 ID 和状态，不保存密钥。新版本用新目录，避免把新图套进旧任务。并发运行前检查同一版本是否已有提交者；写入提交意图并立即持久化返回 ID。

**断点处理**：

- 已有 ID：先查询状态，不再次 POST。
- POST 超时或连接断开且没有 ID：结果不明不代表未创建。先核对本地记录和官方任务列表；无法对应时停在该提交步骤，不能靠重发猜测。
- PENDING / IN_PROGRESS：等待并适度退避，可同时做本地接入准备。
- SUCCEEDED：保存原始产物，检查文件可读性后再进入绑定或动画。
- FAILED：读实际错误，修正输入或配置后在明确的重试范围内操作；额度不足时说明阻塞，不自动购买。
- 下载超时：重试同一产物下载即可，不重新生成。先写临时文件，校验完整再重命名。
- 旧任务 404 或签名链接过期：检查任务保留期、既有本地模型及可刷新的链接；不要把过期误判为密钥错误。

## 已验证接口形状

单图生成：`POST https://api.meshy.ai/openapi/v1/image-to-3d`；`image_url` 可为图片 data URI。返回 `result` 是任务 ID；同路径 `GET /:id` 返回状态、进度及 `model_urls.glb`。

多图生成：`POST https://api.meshy.ai/openapi/v1/multi-image-to-3d`；`image_urls` 提供 1–4 张同一主体的不同视角，第一张作为主正面。正面要优先保证眼睛、口鼻和身份特征；侧面负责体积与前后肢分离；背面负责尾巴、后肢和轮廓。不要用简单镜像替代存在明显左右差异的主体，也不要混入姿势、年龄或毛色不一致的图。

照片单图出现脸部不可读、肢体粘连或背面错误时，先看任务返回的多视图预览。若输入本身有运动遮挡、长毛高光或浅景深，改为干净的建模参考并用多图重试，而不是用同一张图反复提交。默认最多做一次有实质输入改进的重试，旧任务和失败预览保留在版本目录中。

本次人形实例使用 `ai_model=meshy-7`、`ultra_mode=true`、`pose_mode=a-pose`、贴图与 PBR、4K 原始贴图、三角形重拓扑目标 50,000 面、GLB 格式。它是一个实测配置，不是每个角色的预算或质量要求；手机、近景主角和背景 NPC 应分别决定规格。非人形不要套用 A/T pose，通常保持空 `pose_mode`，并按实际用途决定面数和贴图分辨率。

绑定：仅对当前接口明确支持的资产调用 `POST /openapi/v1/rigging`，提供支持的 `input_task_id` 或公开可访问的 `model_url`，并设置符合目标项目的 `height_meters`。URL 输入需符合文档的朝向要求；不要机械照搬实例的 2.27，也不要把四足动物送进人形绑定接口碰碰运气。查询 `GET /openapi/v1/rigging/:id`。

绑定成功后读取实际 `result`：

- `rigged_character_glb_url`：带骨骼模型。
- `basic_animations.walking_glb_url`：本次返回的基础行走资源；若可用可下载整理，不必另付费生成同类动作。
- 其余动画或格式按实际响应选择，不能假设总是存在。

保留原始模型、绑定结果与使用过的基础动作，记录来源。任务响应中的签名 URL 只用于下载，不嵌入游戏作为长期资源地址。
