---
name: media-processing
description: "媒体文件处理：视频截图、视频转 GIF、图片缩放/裁剪/压缩、模糊背景填充，用 FFmpeg 处理视频、Pillow 处理图片。当用户说「截个图」「转 GIF」「缩放图片」「压缩图片」「改成 1920×1080」「视频处理」「图片处理」时使用。"
---

# 媒体文件处理

媒体文件处理：视频截图、视频转 GIF、图片缩放/裁剪/模糊背景填充、批量压缩。

工具链：**FFmpeg**（视频）、**PIL/Pillow**（图片）。两者互补，覆盖常见媒体后处理需求。

## 前置条件

```bash
ffmpeg -version   # 视频处理
ffprobe -version  # 通常随 ffmpeg 安装
pip3 install Pillow  # 图片处理
```

---

## 一、视频截图 (FFmpeg)

从视频中提取单帧或指定时间点的画面。

### 截取单帧

```bash
ffmpeg -y -ss TIMESTAMP -i input.mp4 -vframes 1 -q:v 2 output.png
```

- `-ss` 放在 `-i` 前面：快速定位（seek 到最近关键帧再解码）
- `-vframes 1`：只输出 1 帧
- `-q:v 2`：JPEG 质量（2=高质量，1=最好）；PNG 无需此参数

### 截取多帧（每隔 N 秒）

```bash
ffmpeg -y -i input.mp4 -vf "fps=1/INTERVAL" -q:v 2 output_%03d.png
```

例：每 5 秒截一帧 → `fps=1/5`

### 截取指定分辨率

```bash
ffmpeg -y -ss 10 -i input.mp4 -vframes 1 -vf "scale=1920:-1" output.png
```

### 工作流

1. 用 `ffprobe` 获取视频时长、分辨率
2. 确认用户要截取的时间点：
   - 用户指定时间 → 直接用
   - 用户说"截图"但没说时间 → 建议几个关键时刻（开头、中间、结尾），或直接截中间帧
3. 执行 ffmpeg 截图
4. 把输出图片的路径告诉用户（所用工具支持直接发图就直接发）

### 获取视频信息

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=noprint_wrappers=1 input.mp4
```

### 截图注意事项

- `-ss` 放在 `-i` **前面**（input seeking）比放在后面快很多，但可能不精确到最近关键帧
- 需要精确帧时，把 `-ss` 放在 `-i` **后面**（output seeking），但会更慢
- PNG 无损但文件大，JPG 用 `-q:v 2` 质量足够且文件小
- 输出默认放在输入视频旁边，命名 `<原文件名>_<时间点>.png`；用户指定了位置就按用户的

---

## 二、视频转 GIF (FFmpeg)

使用 ffmpeg 的两遍调色板方案（palettegen + paletteuse），保证颜色质量。

### 核心命令

```bash
ffmpeg -y -i input.mp4 \
  -vf "fps=10,scale=WIDTH:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  -loop 0 \
  output.gif
```

### 参数策略

| 视频时长 | fps | 宽度 | max_colors | 说明 |
|---------|-----|------|------------|------|
| < 5s | 15 | 640 | 256 | 短片段高质量 |
| 5-30s | 12 | 480 | 192 | 平衡质量与大小 |
| > 30s | 10 | 480 | 128 | 长视频压缩优先 |

### 截取片段

```bash
ffmpeg -y -ss 5 -t 10 -i input.mp4 \
  -vf "fps=12,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192[p];[s1][p]paletteuse=dither=bayer" \
  -loop 0 output.gif
```

### GIF 注意事项

- **不加 palettegen** 会导致 GIF 颜色严重失真（默认 256 色不够）
- **分辨率过高** 文件会暴涨，480px 宽是安全默认值
- **MOV 文件** 需确认 ffmpeg 已编译支持（通常没问题）
- 输出默认放在输入视频旁边，同名 `.gif`
- **GIF 太大，模型看不了**：图片识别接口通常有大小上限，GIF 很容易超。用 `ffmpeg -i input.gif -vframes 1 frame.png` 截取单帧再看

---

## 三、图片缩放与裁剪 (PIL/Pillow)

使用 Python PIL/Pillow 进行图片尺寸调整，无需外部服务。

### 场景一：缩放到指定尺寸（可能变形）

```python
from PIL import Image
img = Image.open('input.jpg')
img_resized = img.resize((1920, 1080), Image.LANCZOS)
img_resized.save('output.png')
```

### 场景二：保持内容不变 + 模糊背景填充（推荐）

当原图比例与目标比例不同时，保持原图完整内容，用模糊放大版作为背景：

```python
from PIL import Image, ImageFilter

img = Image.open('input.jpg')
target_w, target_h = 1920, 1080

# 按目标高度缩放原图（保持比例）
ratio = target_h / img.height
new_w = int(img.width * ratio)
new_h = target_h
img_resized = img.resize((new_w, new_h), Image.LANCZOS)

# 模糊背景：拉伸到目标尺寸 + 高斯模糊
bg = img.resize((target_w, target_h), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(radius=30))

# 居中粘贴清晰原图
x_offset = (target_w - new_w) // 2
bg.paste(img_resized, (x_offset, 0))

bg.save('output.png', quality=95)
```

### 场景三：黑边填充

```python
from PIL import Image

img = Image.open('input.jpg')
target_w, target_h = 1920, 1080

ratio = min(target_w / img.width, target_h / img.height)
new_w = int(img.width * ratio)
new_h = int(img.height * ratio)
img_resized = img.resize((new_w, new_h), Image.LANCZOS)

canvas = Image.new('RGB', (target_w, target_h), (0, 0, 0))
x = (target_w - new_w) // 2
y = (target_h - new_h) // 2
canvas.paste(img_resized, (x, y))
canvas.save('output.png')
```

### 常用目标尺寸

| 用途 | 尺寸 |
|------|------|
| 1080p 海报 | 1920×1080 |
| 社交媒体封面 | 1200×630 |
| 微信公众号封面 | 900×383 |
| B 站封面 | 1146×717 |

---

## 四、批量压缩 (PIL/Pillow)

PNG → JPEG quality=80 可压缩 85-90%。

```python
from PIL import Image
import os

wallpaper_dir = "assets/wallpapers"  # 换成实际目录
total_before = 0
total_after = 0

for f in os.listdir(wallpaper_dir):
    if f.endswith('.png'):
        path = os.path.join(wallpaper_dir, f)
        size_before = os.path.getsize(path)
        total_before += size_before

        img = Image.open(path)
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        jpg_path = path.replace('.png', '.jpg')
        img.save(jpg_path, 'JPEG', quality=80, optimize=True)
        size_after = os.path.getsize(jpg_path)
        total_after += size_after

        print(f"{f}: {size_before/1024/1024:.1f}MB -> {size_after/1024/1024:.1f}MB")

print(f"\n总计: {total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB")
```

压缩后需更新代码中的文件路径（.png → .jpg）。

---

## 通用注意事项

- **沙箱里的 Python 可能没装 Pillow**：改在本机终端跑脚本
- **Image.LANCZOS** 是最高质量的缩放滤镜，适合缩小和放大
- **模糊半径** 30 适合大多数场景，更大更模糊
- 原图比目标小时，模糊背景会有明显噪点
- 输出 PNG 保持质量，JPG 用 `quality=95` 平衡大小和质量
- **看图能力不可用时**：用 Pillow 读图片尺寸、模式等元数据先顶上
- **PIL 程序化生成 ≠ AI 绘图**：PIL 只能做渐变/噪声/几何剪影，无法生成真正的美术风格背景。如果用户要 AI 绘图风格，直接说干不了，建议用 Midjourney/SD/DALL-E
- **小图放大（278×188 → 1920×1080）**：原图太小时无论什么填充方案都会糊，先告知用户风险
- **不要默认模糊背景填充**：当原图比目标小很多时效果很差。应列出 3 种方案让用户选：模糊填充、直接拉伸、黑边填充
- **用户说"这是原图"时不要再追问高清版本**，接受当前分辨率，给出最佳方案
- **看图接口报认证错误立刻停手**：只试一次，马上告诉用户

## 参考资料

- `references/image-resize-detailed.md` — 图片尺寸调整的补充：多端壁纸尺寸、方案选择、能力边界
