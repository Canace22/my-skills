---
name: macos-automator-service-fix
description: "修复 macOS Automator Service（.workflow）不在 Finder 右键菜单显示的问题。当用户说「右键菜单里没有我做的服务」「Automator 快速操作不显示」「.workflow 装了但看不到」时使用。"
---

# macOS Automator Service 右键菜单修复

## 触发条件
- 用户说"Finder 右键菜单里没有出现 XX 选项"
- 创建了 `.workflow` 但右键看不到

## 诊断步骤

1. 确认 workflow 文件存在：`~/Library/Services/<名称>.workflow`
2. 检查 `Info.plist` 格式

## 关键坑：旧版 Service 格式的 plist 键

**旧版 Automator Service**（`AMWorkflowType: Service` 格式）的 `Info.plist` 需要这些键：

| 键 | 值 | 说明 |
|---|---|---|
| `NSSendFileTypes` | `["public.item", "public.folder"]` | 支持文件和文件夹。❌ **不能用** `NSSendTypes` / `NSRequiredContext`——这俩是现代 app extension 格式的键，旧版格式根本**不读** |
| `NSMenuItem` | `{"default": "显示的名称"}` | 菜单标题 |
| `CFBundleIdentifier` | 唯一标识（如 `local.user.service-name`） | |
| `CFBundlePackageType` | `AMWF` | Automator Workflow Bundle 类型标识 |
| `NSMessage` | `runWorkflowAsService` | 固定 |

## 注册步骤

```bash
# 1. 刷新 Service 注册
/System/Library/CoreServices/pbs -flush

# 2. 重启 Finder
killall Finder

# 3. 验证注册
/System/Library/CoreServices/pbs -dump | grep -A10 <服务名>
```

## 验证
- `plutil -lint /path/to/Info.plist` 通过
- `pbs -dump` 能看到对应 bundle 和 `NSSendFileTypes`
- Finder 右键文件/文件夹 → 服务 → 菜单名出现

## 注意
- Codex 或 Claude Code 的沙箱可能无法执行 `pbs -flush` 和 `killall Finder`（XPC 权限拒绝），需要手动跑最后两步
- `lsregister -f` 对 `.workflow` 无效（返回 -10811，它不是 .app bundle）
