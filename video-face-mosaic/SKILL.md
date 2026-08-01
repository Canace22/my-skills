---
name: video-face-mosaic
description: 给视频里的人脸批量打码/模糊，可指定保留某个人不打码。当用户说「给视频人脸打码」「打马赛克」「模糊路人的脸」「只保留某某的脸」「视频匿名化」时使用。
---

# 视频人脸打码（可保留指定人物）

给视频里所有人脸打马赛克，并且可以指定**保留某一个人**的脸不打码。

不要用剪辑软件（剪映/CapCut）的「自动人脸打码」来做这件事——它通常最多只处理 3 张脸，会漏、会抖，而且没法排除指定的人。用本目录的脚本，人数不限。

> 配套脚本：[`scripts/facemask.py`](scripts/facemask.py)（本文附录是同一份内容，方便在没有仓库的环境里直接粘贴使用）

---

## 0. 先问清楚

在动手前确认：

- **保留谁？**（描述外貌特征，比如"左边第二个、棕色上衣黑裤子的"）——如果不需要保留任何人就跳过
- **打码样式**：马赛克（默认）还是纯色块 / 高斯模糊
- **输出分辨率**：默认 1080p；源是 4K 时全尺寸渲染会慢好几倍，先确认要不要
- 做完是否直接交付

---

## 1. 检查源视频（**必做，别跳**）

```bash
ffprobe -v error -select_streams v:0 -show_streams -of default=nw=1 IN.mp4 \
  | grep -Ei "codec_name|pix_fmt|width|height|r_frame_rate|color_|dv_profile"
```

重点看 `color_transfer`：

| 值 | 含义 | 处理方式 |
|---|---|---|
| `bt709` 或空 | 普通 SDR | 正常处理 |
| `arib-std-b67` | **HLG HDR**（手机拍的常见） | 必须走 HDR 分支 |
| `smpte2084` | **PQ / HDR10** | 必须走 HDR 分支 |

⚠️ **最容易踩的坑**：HDR 素材如果按普通流程解成 8bit RGB 再编码，色彩元数据会丢，播放器把 BT.2020 数据当 BT.709 显示，成片会**发灰、发白、对比度和饱和度都掉一截**。脚本的 `--hdr auto` 会自动识别并用 16bit 管线 + 保留元数据的 HEVC 10bit 输出，别关掉它。

（`dv_profile` 是 Dolby Vision，RPU 层会丢，但 HLG/PQ 基础层保住了，播放正常。）

---

## 2. 装依赖

```bash
pip install deface --break-system-packages -q
```

`deface` 自带 `centerface.onnx`（CenterFace，WIDER FACE 训练，侧脸/遮挡/小脸都能检），装完即用，**不需要联网下模型**。系统需要有 `ffmpeg` 和 `opencv-python`。

---

## 3. 四步走

沙盒里单条命令通常有 ~45 秒上限，所以 `detect` 和 `render` 都支持**断点续跑**：
跑到 `--budget` 秒就存盘退出，**重复执行同一条命令**直到打印 `STEP DONE`。

### 3.1 检测

```bash
python3 scripts/facemask.py detect --input IN.mp4 --work /tmp/fm/w
# 输出 STEP INCOMPLETE 就再跑一遍同样的命令
```

参考速度：1280×720 检测约 11 fps。60fps 的 32 秒片（1935 帧）≈ 3 分钟，5～6 次调用。

### 3.2 看参考帧，确定保留谁

```bash
python3 scripts/facemask.py plan --input IN.mp4 --work /tmp/fm/w --preview-frames 300,900,1500
```

会在 `工作目录/preview/` 生成带标注的图，每个框上写着 `轨迹ID (中心x, 中心y)`。
**把图看一遍**，找到要保留的那个人，记下她的**中心坐标**和所在**帧号**。
拿不准是哪个人时，把这张图给用户确认。

### 3.3 生成打码方案

```bash
python3 scripts/facemask.py plan --input IN.mp4 --work /tmp/fm/w \
  --keep-frame 900 --keep-xy 462,413
```

看输出的「保留目标覆盖 N/M 帧」——覆盖率低于 80% 说明跟丢了，换一个人脸更清楚的帧重选坐标。
不需要保留任何人就省掉 `--keep-*` 参数。

### 3.4 渲染

```bash
python3 scripts/facemask.py render --input IN.mp4 --work /tmp/fm/w --output OUT.mp4
# 同样：STEP INCOMPLETE 就重复执行
```

常用参数：

- `--height 1080`（默认）/ `--height 0` 保持原分辨率
- `--crf 20` 画质，`--preset ultrafast` 速度（HDR 走 libx265，慢，ultrafast 约 14 fps）
- `--pad 0.30` 打码区域外扩比例，`--blocks 12` 马赛克格子数（越小越糊）

音轨自动从源片复制。

---

## 4. 验收（**必做**）

抽几帧检查，别只看缩略图——脸在整幅画面里很小，要放大裁剪看：

```bash
for t in 3 10 20 30; do
  ffmpeg -v error -ss $t -i OUT.mp4 -frames:v 1 -vf "crop=1600:280:200:480" /tmp/fm/chk_$t.png -y
done
```

拼成一张长图看。逐项确认：

1. 每张该打的脸都打上了，没有漏帧闪脸
2. 要保留的人全程清晰，没有中途被误打码
3. **颜色和原片一致**——HDR 素材要用同一条 tonemap 把原片和成片都转成 SDR 再比：
   ```bash
   TM="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=rgb24"
   ffmpeg -v error -ss 16 -i IN.mp4  -frames:v 1 -vf "scale=960:540,$TM" /tmp/fm/a.png -y
   ffmpeg -v error -ss 16 -i OUT.mp4 -frames:v 1 -vf "scale=960:540,$TM" /tmp/fm/b.png -y
   ```
   两张图的 BGR 均值和标准差应该几乎一样。
4. 时长、帧数和源片一致

---

## 5. 常见问题

| 现象 | 原因 / 处理 |
|---|---|
| 成片发灰发白、颜色不对 | HDR 元数据丢了。确认 `--hdr auto` 生效，`ffprobe` 检查成片的 `color_transfer` 是否和源片一致 |
| 有人脸没打上 | 降 `--thresh`（0.30 → 0.22）重跑 detect；或调大 `--det-width` 到 1600 |
| 墙面/图案被误打码 | 提高 `--thresh`，或提高 `plan` 的 `--min-len` 只保留长轨迹 |
| 打码有闪烁 | `plan` 里已经做了 45 帧内的插值补帧；仍闪就把 `--max-move` 调大一点 |
| 保留的人中途被打码 | 覆盖率不够，换个正脸清楚的帧重设 `--keep-frame/--keep-xy` |
| 镜子/多机位里同一个人出现两次 | 脚本只跟踪一条轨迹。另一处会被打码——先跟用户确认这样行不行 |
| 渲染太慢 | 降 `--height`，或 `--preset ultrafast`；HDR 的 libx265 10bit 本身就比 SDR 慢一倍多 |

---

## 6. 原理速览

1. **检测**：CenterFace 在降采样帧上逐帧跑，只输出人脸框，不做识别
2. **跟踪**：按"离上一帧最近"把框串成轨迹（60fps 下帧间位移很小，这个笨办法最稳），短暂漏检用线性插值补上
3. **锁定保留对象**：在指定帧手动指认一次，然后前后双向传播；每帧把落在该位置的框从打码列表剔除
4. **渲染**：检测走小分辨率、渲染走目标分辨率，坐标按比例换算；HDR 走 16bit 管线并把色彩元数据原样写回

---

## 附录：facemask.py

与 [`scripts/facemask.py`](scripts/facemask.py) 内容一致。

```python
#!/usr/bin/env python3
"""视频人脸打码 —— 检测/跟踪/渲染三步，可指定保留某个人的脸。

设计要点：
- 沙盒里单次命令有时间上限，所以每一步都支持断点续跑：
  跑到 --budget 秒就保存进度退出，重复执行同一条命令直到打印 STEP DONE。
- 检测走小分辨率（快），渲染走目标分辨率（清晰），坐标按比例换算。
- HDR 素材保留原色彩元数据，避免颜色被改。
"""
import argparse, json, os, subprocess, sys, time
import numpy as np, cv2

# ---------- 通用小工具 ----------
def probe(path):
    keys = "width,height,r_frame_rate,nb_frames,pix_fmt,color_space,color_transfer,color_primaries,color_range"
    out = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                          "-show_entries",f"stream={keys}","-of","json",path],
                         capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    s["fps"] = float(num)/float(den)
    return s

def state_path(work): return os.path.join(work, "state.json")

def load_state(work):
    p = state_path(work)
    return json.load(open(p)) if os.path.exists(p) else {}

def save_state(work, st):
    json.dump(st, open(state_path(work), "w"))

def center(b): return ((b[0]+b[2])/2.0, (b[1]+b[3])/2.0)

# ---------- 1. 检测 ----------
def cmd_detect(a):
    from deface.centerface import CenterFace
    os.makedirs(a.work, exist_ok=True)
    info = probe(a.input)
    W = a.det_width; H = int(round(info["height"]*W/info["width"]/2))*2
    st = load_state(a.work)
    st.update(det_w=W, det_h=H, fps=info["fps"], src_w=info["width"], src_h=info["height"])
    dets = json.load(open(f"{a.work}/dets.json")) if os.path.exists(f"{a.work}/dets.json") else []
    start_f = len(dets)

    cf = CenterFace(in_shape=None, backend="auto")
    t_start = start_f/info["fps"]
    dec = subprocess.Popen(["ffmpeg","-v","error","-ss",f"{t_start:.6f}","-i",a.input,
                            "-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","bgr24","-"],
                           stdout=subprocess.PIPE, bufsize=10**8)
    t0 = time.time(); n = 0; buf = b""
    while time.time()-t0 < a.budget:
        buf = dec.stdout.read(W*H*3)
        if len(buf) < W*H*3: break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        d, _ = cf(f, threshold=a.thresh)
        dets.append([[round(float(v),2) for v in b] for b in d]); n += 1
    dec.kill()
    json.dump(dets, open(f"{a.work}/dets.json","w"))
    done = n == 0 or (len(buf) < W*H*3)
    st["detect_done"] = bool(done); save_state(a.work, st)
    print(f"detect: +{n} frames, total {len(dets)}")
    print("STEP DONE" if done else "STEP INCOMPLETE — 再跑一次同样的命令")

# ---------- 2. 跟踪 + 选目标 ----------
def build_tracks(frames, maxd):
    tracks, nxt = [], 0
    for fi, dets in enumerate(frames):
        cands = [(d, center(d)) for d in dets]
        pairs = []
        for ti, t in enumerate(tracks):
            if fi - t["last_f"] > 30: continue
            for ci, (d, c) in enumerate(cands):
                dist = ((c[0]-t["last_c"][0])**2 + (c[1]-t["last_c"][1])**2)**.5
                if dist < maxd: pairs.append((dist, ti, ci))
        pairs.sort(); tk, used = set(), set()
        for dist, ti, ci in pairs:
            if ti in tk or ci in used: continue
            tk.add(ti); used.add(ci)
            d, c = cands[ci]
            tracks[ti]["boxes"][fi] = d; tracks[ti]["last_c"] = c; tracks[ti]["last_f"] = fi
        for ci, (d, c) in enumerate(cands):
            if ci in used: continue
            tracks.append({"id": nxt, "last_c": c, "last_f": fi, "boxes": {fi: d}}); nxt += 1
    return tracks

def interp(boxes, max_gap=45):
    fs = sorted(boxes); out = {}
    for a_, b_ in zip(fs, fs[1:]):
        out[a_] = boxes[a_]
        if 1 < b_-a_ <= max_gap:
            A = np.array(boxes[a_][:4]); B = np.array(boxes[b_][:4])
            for k in range(1, b_-a_):
                out[a_+k] = list(A + (B-A)*k/(b_-a_)) + [0.0]
    out[fs[-1]] = boxes[fs[-1]]
    return out

def cmd_plan(a):
    frames = json.load(open(f"{a.work}/dets.json")); N = len(frames)
    st = load_state(a.work)
    tracks = build_tracks(frames, a.max_move)
    tracks = [t for t in tracks if len(t["boxes"]) >= a.min_len]
    tracks.sort(key=lambda t: -len(t["boxes"]))
    print("长轨迹：", [(t["id"], len(t["boxes"])) for t in tracks[:12]])

    if a.preview_frames:
        _preview(a, frames, tracks)

    target = {}
    if a.keep_xy:
        kx, ky = [float(v) for v in a.keep_xy.split(",")]
        kf = a.keep_frame if a.keep_frame is not None else N//2
        if not frames[kf]: sys.exit("keep_frame 上没有任何检测框")
        seed = min(frames[kf], key=lambda b: (center(b)[0]-kx)**2 + (center(b)[1]-ky)**2)
        target[kf] = seed
        for rng in (range(kf-1, -1, -1), range(kf+1, N)):
            last = center(seed); miss = 0
            for fi in rng:
                best, bd = None, 1e9
                for b in frames[fi]:
                    c = center(b); d = ((c[0]-last[0])**2 + (c[1]-last[1])**2)**.5
                    if d < bd: bd, best = d, b
                if best is not None and bd < a.max_move*0.75 + 2.5*miss:
                    target[fi] = best; last = center(best); miss = 0
                else:
                    miss += 1
                    if miss > 90: break
        print(f"保留目标覆盖 {len(target)}/{N} 帧")

    filled = [interp(t["boxes"]) for t in tracks]
    out = []
    for fi in range(N):
        boxes = [fl[fi][:4] for fl in filled if fi in fl]
        for b in frames[fi]:
            c = center(b)
            if all(((c[0]-(x[0]+x[2])/2)**2 + (c[1]-(x[1]+x[3])/2)**2)**.5 > 35 for x in boxes):
                boxes.append(b[:4])
        tb = target.get(fi)
        if tb is not None:
            tc = center(tb)
            boxes = [x for x in boxes if ((tc[0]-(x[0]+x[2])/2)**2 + (tc[1]-(x[1]+x[3])/2)**2)**.5 > 30]
        out.append([[round(v,1) for v in b] for b in boxes])
    json.dump(out, open(f"{a.work}/boxes.json","w"))
    st["plan_done"] = True; save_state(a.work, st)
    print("平均每帧打码框：", round(sum(len(b) for b in out)/N, 2))
    print("STEP DONE")

def _preview(a, frames, tracks):
    st = load_state(a.work); W, H = st["det_w"], st["det_h"]; fps = st["fps"]
    os.makedirs(f"{a.work}/preview", exist_ok=True)
    for fi in [int(x) for x in a.preview_frames.split(",")]:
        raw = subprocess.run(["ffmpeg","-v","error","-ss",f"{fi/fps:.6f}","-i",a.input,
                              "-frames:v","1","-vf",f"scale={W}:{H}",
                              "-f","rawvideo","-pix_fmt","bgr24","-"], capture_output=True).stdout
        if len(raw) < W*H*3: continue
        img = np.frombuffer(raw[:W*H*3], np.uint8).reshape(H, W, 3).copy()
        for tr in tracks:
            b = tr["boxes"].get(fi)
            if not b: continue
            x1,y1,x2,y2 = [int(v) for v in b[:4]]
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(img,f"{tr['id']} ({(x1+x2)//2},{(y1+y2)//2})",(x1,y1-6),0,0.5,(0,0,255),2)
        cv2.imwrite(f"{a.work}/preview/f{fi}.jpg", img, [cv2.IMWRITE_JPEG_QUALITY,90])
    print(f"参考帧已写到 {a.work}/preview/（框上是 轨迹ID (中心x,中心y)）")

# ---------- 3. 渲染 ----------
def mosaic(img, boxes, scale, pad, blocks):
    H, W = img.shape[:2]
    for b in boxes:
        x1,y1,x2,y2 = [v*scale for v in b]
        w, h = x2-x1, y2-y1
        x1 -= w*pad; x2 += w*pad; y1 -= h*pad*1.4; y2 += h*pad
        x1 = max(0,int(x1)); y1 = max(0,int(y1)); x2 = min(W,int(x2)); y2 = min(H,int(y2))
        if x2 <= x1 or y2 <= y1: continue
        roi = img[y1:y2, x1:x2]
        bw = max(1,(x2-x1)//blocks); bh = max(1,(y2-y1)//blocks)
        sm = cv2.resize(roi,(max(1,(x2-x1)//bw), max(1,(y2-y1)//bh)), interpolation=cv2.INTER_AREA)
        img[y1:y2, x1:x2] = cv2.resize(sm,(x2-x1,y2-y1), interpolation=cv2.INTER_NEAREST)
    return img

def cmd_render(a):
    st = load_state(a.work); boxes = json.load(open(f"{a.work}/boxes.json"))
    info = probe(a.input); fps = st["fps"]
    H = a.height or info["height"]; W = int(round(info["width"]*H/info["height"]/2))*2
    scale = W/float(st["det_w"])
    hdr = (a.hdr == "on") or (a.hdr == "auto" and (info.get("color_transfer") in ("arib-std-b67","smpte2084")))
    segdir = f"{a.work}/seg"; os.makedirs(segdir, exist_ok=True)
    done = st.get("render_frames", 0)
    if done >= len(boxes):
        return _finish(a, st, info, hdr)

    idx = st.get("render_seg", 0)
    pix, bpp = ("rgb48le", 6) if hdr else ("bgr24", 3)
    FS = W*H*bpp
    dec = subprocess.Popen(["ffmpeg","-v","error","-ss",f"{done/fps:.6f}","-i",a.input,
                            "-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt",pix,"-"],
                           stdout=subprocess.PIPE, bufsize=10**8)
    if hdr:
        cp = info.get("color_primaries","bt2020"); tr = info.get("color_transfer","arib-std-b67")
        cm = info.get("color_space","bt2020nc")
        enc_args = ["-c:v","libx265","-preset",a.preset,"-crf",str(a.crf),"-pix_fmt","yuv420p10le",
                    "-color_primaries",cp,"-color_trc",tr,"-colorspace",cm,"-color_range","tv",
                    "-x265-params",f"colorprim={cp}:transfer={tr}:colormatrix={cm}:range=limited",
                    "-tag:v","hvc1"]
    else:
        enc_args = ["-c:v","libx264","-preset",a.preset,"-crf",str(a.crf),"-pix_fmt","yuv420p"]
    seg = f"{segdir}/s{idx:03d}.mp4"
    enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt",pix,
                            "-s",f"{W}x{H}","-r",str(fps),"-i","-","-an"] + enc_args + [seg],
                           stdin=subprocess.PIPE)
    dt = np.uint16 if hdr else np.uint8
    t0 = time.time(); n = 0
    while time.time()-t0 < a.budget:
        buf = dec.stdout.read(FS)
        if len(buf) < FS: break
        img = np.frombuffer(buf, dt).reshape(H, W, 3).copy()
        fi = done + n
        if fi < len(boxes): mosaic(img, boxes[fi], scale, a.pad, a.blocks)
        enc.stdin.write(img.tobytes()); n += 1
    dec.kill(); enc.stdin.close(); enc.wait()
    st["render_frames"] = done + n; st["render_seg"] = idx + 1
    st["hdr"] = hdr; save_state(a.work, st)
    print(f"render: +{n} frames, total {st['render_frames']}/{len(boxes)}")
    if st["render_frames"] >= len(boxes):
        _finish(a, st, info, hdr)
    else:
        print("STEP INCOMPLETE — 再跑一次同样的命令")

def _finish(a, st, info, hdr):
    segdir = f"{a.work}/seg"
    segs = sorted(os.listdir(segdir))
    with open(f"{a.work}/list.txt","w") as f:
        for s in segs: f.write(f"file '{os.path.join(segdir,s)}'\n")
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0",
                    "-i",f"{a.work}/list.txt","-c","copy",f"{a.work}/video.mp4"], check=True)
    cmd = ["ffmpeg","-v","error","-y","-i",f"{a.work}/video.mp4","-i",a.input,
           "-map","0:v","-map","1:a?","-c:v","copy","-c:a","aac","-b:a","192k",
           "-movflags","+faststart","-shortest"]
    if hdr:
        cmd += ["-tag:v","hvc1",
                "-color_primaries",info.get("color_primaries","bt2020"),
                "-color_trc",info.get("color_transfer","arib-std-b67"),
                "-colorspace",info.get("color_space","bt2020nc")]
    subprocess.run(cmd + [a.output], check=True)
    print(f"输出：{a.output}")
    print("STEP DONE")

# ---------- CLI ----------
def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect"); d.set_defaults(fn=cmd_detect)
    d.add_argument("--input", required=True); d.add_argument("--work", required=True)
    d.add_argument("--det-width", type=int, default=1280)
    d.add_argument("--thresh", type=float, default=0.30)
    d.add_argument("--budget", type=float, default=35)

    q = sub.add_parser("plan"); q.set_defaults(fn=cmd_plan)
    q.add_argument("--input"); q.add_argument("--work", required=True)
    q.add_argument("--keep-xy", help="要保留的脸在参考帧上的中心坐标 x,y（检测分辨率下）")
    q.add_argument("--keep-frame", type=int)
    q.add_argument("--preview-frames", help="逗号分隔的帧号，输出带轨迹ID的参考图")
    q.add_argument("--min-len", type=int, default=150)
    q.add_argument("--max-move", type=float, default=60)

    r = sub.add_parser("render"); r.set_defaults(fn=cmd_render)
    r.add_argument("--input", required=True); r.add_argument("--work", required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--height", type=int, default=1080, help="0 表示保持原分辨率")
    r.add_argument("--hdr", choices=["auto","on","off"], default="auto")
    r.add_argument("--crf", type=int, default=20)
    r.add_argument("--preset", default="ultrafast")
    r.add_argument("--pad", type=float, default=0.30)
    r.add_argument("--blocks", type=int, default=12)
    r.add_argument("--budget", type=float, default=35)

    a = p.parse_args(); a.fn(a)

if __name__ == "__main__":
    main()
```
