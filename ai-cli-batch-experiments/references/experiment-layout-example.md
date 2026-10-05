# 示例：AI 页面风格趋同实验的目录约定

新实验可以照这个结构搭，TASK.md 写流程总纲，extract.py 负责特征提取。

## 目录约定

- `prompts/`：A/B/C 组 × landing/dash/settings 共 9 个 prompt；用一个 `setup_prompts.sh` 可重建（实验期间不改 prompt 内容）
- `runs/`：`<组>-<页面>-<工具>-<次数>.html`，组 A/B/C，页面 landing/dash/settings，工具 claude/codex，次数 1-3
- `shots/`：与 runs 同名 .png
- `records.csv`：extract.py 输出 + 手填「布局骨架」列
- `raw/`：原始输出存档（.txt 输出 / .err stderr）

## 分阶段

1. 第一阶段：A-landing × 2 工具 × 3 次 = 6 个 HTML + CSV + 截图，跑完停下来等确认
2. 第二阶段：A-dash/A-settings + B/C-landing，共 24 次；`records.csv` 追加，不重复写表头
3. 全部 30 个 HTML

## extract.py 字段

自动：主色HEX、是否渐变、首选字体、圆角px、阴影层数、图标方式、间距基数px、深色模式、含emoji、代码行数
手填：布局骨架（同结构同字符串，示例：`导航+hero+3卡+CTA`、`hero+3卡+CTA`、`导航+hero+3卡+页脚`）

## 截图规范

1280 宽视口（height 800），整页截图 full_page=True（用 `scripts/screenshot_html.py`）。
