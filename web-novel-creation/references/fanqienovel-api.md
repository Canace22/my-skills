# 番茄小说 API 参考

## 分类列表 API

**Endpoint**: `GET https://fanqienovel.com/api/author/book/category_list/v0/`

**Headers**: `User-Agent: Mozilla/5.0`

**Response**: JSON with `code`, `data`, `message` fields.

### Data Structure
```json
{
  "code": 0,
  "data": [
    {
      "category_id": 262,
      "label": "主分类",  // or "主题", "角色", "情节"
      "name": "都市脑洞",
      "cover_uri": "http://...",
      "description": "拥有金手指系统的男频都市脑洞奇想"
    }
  ],
  "message": "success"
}
```

### Labels (分类层级)
- **主分类** (36个): Top-level genre categories
- **主题** (~60个): Themes and settings
- **角色** (~50个): Character archetypes
- **情节** (~80个): Plot elements and tropes

### Key 主分类 (Main Categories)

| ID | Name | Description |
|---|---|---|
| 262 | 都市脑洞 | 拥有金手指系统的男频都市脑洞奇想 |
| 258 | 传统玄幻 | 废柴逆袭，强者重生等传统玄幻 |
| 539 | 悬疑脑洞 | 脑洞向悬疑灵异、规则怪谈等 |
| 746 | 游戏体育 | 网游、竞技及穿入游戏或世界游戏化 |
| 748 | 豪门总裁 | 豪门言情，霸总、打脸爽文 |
| 23 | 种田 | 种田、空间、经商、基建等古言文 |
| 24 | 快穿 | 主角依次穿越多个小世界完成任务 |
| 79 | 年代 | 穿越年代、重生年代、空间金手指 |
| 8 | 科幻末世 | 末世、丧尸、星际、机甲等 |
| 124 | 都市修真 | 以修真为力量体系的都市文 |
| 1014 | 都市高武 | 都市架空，全民修炼体系、灵气复苏 |
| 27 | 战神赘婿 | 都市向战神，兵王文 |

### Key 情节 (Plot Tags)

Popular tags for male-oriented:
- 系统(19), 重生(36), 穿越(37), 打脸(522), 升级流(830)
- 诸天万界(71), 无限流(70), 末世(68), 直播(69)
- 无敌(384), 逆袭, 神豪(20), 鉴宝(17)

Popular tags for female-oriented:
- 甜宠(96), 虐文(95), 先婚后爱(265), 追妻火葬场(616)
- 马甲(266), 真假千金(844), 穿书(382), 快穿(24)
- 种田(23), 宫斗宅斗, 医术(247)

## Book List API (推测)

Hot list page: `https://fanqienovel.com/library/male?sort=hot`

⚠️ HTML rendering has encoding issues. The API may have a separate endpoint for book lists but wasn't discovered in this session. The category list API is confirmed working.
