# 续写工作流参考

## 项目发现模式

当用户说"继续更新 <项目名>"时，按以下顺序：

1. **查历史上下文**（工具支持搜索过往会话就搜一下）— 找到之前写到哪了、有什么约定
2. **检查 AGENTS.md** — 项目根目录是否有自定义规则
3. **检查 project.yaml** — 当前进度（current_volume, current_chapter）
4. **检查最近章节元数据** — 了解上下文（一次批量读取）
5. **检查章纲** — 下一章是否有详细大纲

## 批量写入效率模式

❌ 低效（每章 3 次调用）：
```
write 第23章 → write 第23章元数据 → sync fanon
write 第24章 → write 第24章元数据 → sync fanon
write 第25章 → write 第25章元数据 → sync fanon
update yaml + readme
```

✅ 高效（批量写入 + 1 次 fanon 同步）：
```
一次写完 3 章正文
一次写完 3 个元数据文件
patch fanon/新人物.md
patch fanon/关系进度.md
patch project.yaml
patch README.md
```

## 章纲创建模式

当只有卷大纲（大纲.md）没有章纲（章纲.md）时，章纲需要包含：
- 每章的四件套：主推进、主冲突层、节奏位、章末钩子类型
- 一句话事件
- 必出现的人物/物/设定
- 信息差体现（如果是智斗/重生类）
- 节奏设计（前中后段安排）

## 卷过渡检查清单

当 current_chapter 到达卷大纲的最后一个章节：
1. 在最后一章末尾加 `# 卷N《卷名》完`
2. 创建下一卷的 大纲.md（如果不存在）
3. 创建下一卷的 章纲.md（至少前 3-4 章）
4. 更新 project.yaml 的 current_volume 和 current_chapter
5. 更新 README.md 进度表

## 编号约定

- 全局 skill 模板用 `第NNN章`（3位补零）
- 实际项目可能用 `第NN章`（2位）或 `第N章`（不补零）
- **以项目已有文件的命名为准**，不要改变编号格式
- 用 `ls chapters/` 检查项目实际使用的格式
