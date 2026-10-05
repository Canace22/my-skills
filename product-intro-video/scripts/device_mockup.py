#!/usr/bin/env python3
"""Composite a screenshot into a device mockup (browser / laptop / phone).

Pure Pillow, no external assets. Output is a PNG; background is transparent
unless --bg is given.

Examples:
    python device_mockup.py --input shot.png --frame laptop --output out.png
    python device_mockup.py -i shot.png -f phone -o out.png --bg "#0e1116"
    python device_mockup.py -i shot.png -f browser -o out.png --pad 80
"""
import argparse
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required: pip install pillow --break-system-packages")


def rounded_mask(size, radius):
    """An L-mode mask with a filled rounded rectangle."""
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def paste_rounded(canvas, img, xy, radius):
    """Paste img onto canvas at xy, clipping img to rounded corners."""
    canvas.paste(img, xy, rounded_mask(img.size, radius))


def browser_frame(shot):
    """macOS-style window: title bar with three dots, screenshot below."""
    w, h = shot.size
    bar = max(28, round(w * 0.038))
    radius = max(10, round(w * 0.012))
    dot_r = max(4, round(bar * 0.18))
    win = Image.new("RGBA", (w, h + bar), (0, 0, 0, 0))

    body = Image.new("RGBA", (w, h + bar), (43, 45, 49, 255))
    win.paste(body, (0, 0), rounded_mask(body.size, radius))

    draw = ImageDraw.Draw(win)
    cy = bar // 2
    for i, color in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        cx = round(bar * 0.55) + i * dot_r * 3
        draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=color)

    # screenshot fills the content area; re-clip bottom corners to the window
    win.paste(shot.convert("RGBA"), (0, bar))
    win.putalpha(rounded_mask(win.size, radius))
    return win


def laptop_frame(shot):
    """Screen bezel around the shot, plus a base deck below."""
    w, h = shot.size
    bezel = max(10, round(w * 0.018))
    radius = max(10, round(w * 0.012))
    screen_w, screen_h = w + bezel * 2, h + bezel * 2

    base_h = max(10, round(h * 0.05))
    overhang = round(screen_w * 0.09)
    total_w = screen_w + overhang * 2
    canvas = Image.new("RGBA", (total_w, screen_h + base_h), (0, 0, 0, 0))

    screen = Image.new("RGBA", (screen_w, screen_h), (17, 17, 19, 255))
    screen.paste(shot.convert("RGBA"), (bezel, bezel))
    canvas.paste(screen, (overhang, 0), rounded_mask(screen.size, radius))

    draw = ImageDraw.Draw(canvas)
    top = screen_h
    draw.rounded_rectangle(
        [0, top, total_w - 1, top + base_h - 1],
        radius=round(base_h * 0.35), fill=(200, 204, 210, 255),
    )
    # hinge notch
    notch_w = round(total_w * 0.12)
    nx = (total_w - notch_w) // 2
    draw.rounded_rectangle(
        [nx, top, nx + notch_w, top + round(base_h * 0.4)],
        radius=round(base_h * 0.2), fill=(150, 155, 162, 255),
    )
    return canvas


def phone_frame(shot):
    """Rounded slab with a notch; screenshot clipped inside."""
    w, h = shot.size
    border = max(10, round(w * 0.05))
    radius = round(w * 0.14)
    body_w, body_h = w + border * 2, h + border * 2
    body = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))

    slab = Image.new("RGBA", (body_w, body_h), (17, 17, 19, 255))
    body.paste(slab, (0, 0), rounded_mask(slab.size, radius))

    inner_radius = max(6, radius - border)
    paste_rounded(body, shot.convert("RGBA"), (border, border), inner_radius)

    draw = ImageDraw.Draw(body)
    notch_w, notch_h = round(body_w * 0.32), round(border * 1.1)
    nx = (body_w - notch_w) // 2
    draw.rounded_rectangle(
        [nx, border - 2, nx + notch_w, border - 2 + notch_h],
        radius=notch_h // 2, fill=(17, 17, 19, 255),
    )
    return body


FRAMES = {"browser": browser_frame, "laptop": laptop_frame, "phone": phone_frame}


def add_shadow(img, blur=24, offset=10, alpha=110):
    """Soft drop shadow behind an RGBA image."""
    from PIL import ImageFilter
    pad = blur * 2 + offset
    layer = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    silhouette = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    layer.paste(silhouette, (pad, pad + offset), img.getchannel("A"))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(img, (pad, pad))
    return layer


def main():
    ap = argparse.ArgumentParser(description="Composite a screenshot into a device mockup.")
    ap.add_argument("-i", "--input", required=True, help="source screenshot (PNG/JPG)")
    ap.add_argument("-f", "--frame", required=True, choices=FRAMES, help="mockup style")
    ap.add_argument("-o", "--output", required=True, help="output PNG path")
    ap.add_argument("--bg", default=None, help="background color, e.g. '#0e1116' (default transparent)")
    ap.add_argument("--pad", type=int, default=60, help="padding around the mockup in px (default 60)")
    ap.add_argument("--scale", type=float, default=1.0, help="scale the screenshot before framing")
    ap.add_argument("--no-shadow", action="store_true", help="disable the drop shadow")
    args = ap.parse_args()

    shot = Image.open(args.input).convert("RGBA")
    if args.scale != 1.0:
        shot = shot.resize((round(shot.width * args.scale), round(shot.height * args.scale)))

    mock = FRAMES[args.frame](shot)
    if not args.no_shadow:
        mock = add_shadow(mock)

    pad = args.pad
    size = (mock.width + pad * 2, mock.height + pad * 2)
    bg = (0, 0, 0, 0) if args.bg is None else args.bg
    canvas = Image.new("RGBA", size, bg)
    canvas.alpha_composite(mock, (pad, pad))
    canvas.save(args.output)
    print(f"wrote {args.output}  ({canvas.width}x{canvas.height})")


if __name__ == "__main__":
    main()
