#!/usr/bin/env python3
"""视频人脸打码 —— 检测/跟踪/渲染三步，可指定保留某个人的脸。

设计要点：
- 沙盒里单次命令有时间上限，所以每一步都支持断点续跑：
  跑到 --budget 秒就保存进度退出，重复执行同一条命令直到打印 STEP DONE。
- 检测走小分辨率（快），渲染走目标分辨率（清晰），坐标按比例换算。
- HDR 素材保留原色彩元数据，避免颜色被改（见 SKILL.md）。

用法：
  python3 facemask.py detect  --input IN.mp4 --work DIR [--det-width 1280] [--thresh 0.30]
  python3 facemask.py plan    --work DIR [--keep-frame N --keep-xy X,Y] [--preview-frames a,b,c]
  python3 facemask.py render  --input IN.mp4 --work DIR --output OUT.mp4 [--height 1080] [--hdr auto]
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
    total = int(round(info["fps"]*float(info.get("duration") or 0))) or None

    cf = CenterFace(in_shape=None, backend="auto")
    t_start = start_f/info["fps"]
    dec = subprocess.Popen(["ffmpeg","-v","error","-ss",f"{t_start:.6f}","-i",a.input,
                            "-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","bgr24","-"],
                           stdout=subprocess.PIPE, bufsize=10**8)
    t0 = time.time(); n = 0
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

    # 目标轨迹：从 keep_frame 处离 keep_xy 最近的检测出发，前后双向传播
    target = {}
    if a.keep_xy:
        kx, ky = [float(v) for v in a.keep_xy.split(",")]
        kf = a.keep_frame if a.keep_frame is not None else N//2
        seed = min(frames[kf], key=lambda b: (center(b)[0]-kx)**2 + (center(b)[1]-ky)**2, default=None)
        if seed is None: sys.exit("keep_frame 上没有任何检测框")
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
        for b in frames[fi]:                      # 补上没进长轨迹的零散检测
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
    """输出带轨迹 ID 的参考帧，用来肉眼确认要保留谁。"""
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
    print(f"参考帧已写到 {a.work}/preview/（框上的数字是 轨迹ID (中心x,中心y)）")

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
        enc_args = ["-c:v","libx265","-preset",a.preset,"-crf",str(a.crf),"-pix_fmt","yuv420p10le",
                    "-color_primaries",info.get("color_primaries","bt2020"),
                    "-color_trc",info.get("color_transfer","arib-std-b67"),
                    "-colorspace",info.get("color_space","bt2020nc"),"-color_range","tv",
                    "-x265-params",
                    f"colorprim={info.get('color_primaries','bt2020')}:"
                    f"transfer={info.get('color_transfer','arib-std-b67')}:"
                    f"colormatrix={info.get('color_space','bt2020nc')}:range=limited",
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
    q.add_argument("--keep-xy", help="要保留的那张脸在参考帧上的中心坐标 x,y（检测分辨率下）")
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
