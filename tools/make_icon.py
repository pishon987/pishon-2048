#!/usr/bin/env python3
"""Renders the Christmas 2048 launcher icon.

Outputs (relative to the given out dir):
  512.png            Play Store listing icon (512x512, no transparency)
  full_512.png       same art, used for the legacy mipmaps
  foreground.png     adaptive-icon foreground (432x432, transparent, safe zone)
  preview.png        512 master + 96/64/48 downsamples side by side

Run:  python3 make_icon.py <outdir>
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 4                                  # supersample factor
BASE = 512                              # master icon size
S = BASE * SS                           # working canvas

FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

NIGHT_TOP = (18, 74, 54)
NIGHT_BOTTOM = (4, 16, 12)
PINE_LIGHT = (44, 154, 98)
PINE = (30, 122, 76)
PINE_DARK = (14, 74, 52)
GOLD = (232, 194, 106)
GOLD_BRIGHT = (246, 218, 150)
CREAM = (252, 244, 226)
CREAM_DEEP = (228, 197, 128)
RED_LIGHT = (234, 48, 74)
RED_DARK = (137, 17, 39)
SNOW = (240, 249, 245)

# Layout in master (512 px) coordinates, so the numbers stay readable.
STAR_CY = 100
STAR_R = 30
TREE_TOP = 138
TREE_BOTTOM = 330
NUM_CY = 412
NUM_W = BASE * 0.66


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(size, top, bottom):
    img = Image.new("RGB", (1, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        d.point((0, y), lerp(top, bottom, y / max(1, size - 1)))
    return img.resize((size, size), Image.BILINEAR)


def radial_alpha(size, center, radius, peak=255):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    steps = 64
    for i in range(steps, 0, -1):
        t = i / steps
        a = int(peak * (1 - t) ** 2)
        r = radius * t
        if a > 0 and r > 0:
            d.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], fill=a)
    return mask.filter(ImageFilter.GaussianBlur(radius * 0.05))


def squircle(size, radius_ratio=0.225):
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=255
    )
    return mask


class Rand:
    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFF

    def next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF


def snow_dots(size):
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rnd = Rand(11)
    placed = 0
    while placed < 30:
        x, y = rnd.next() * size, rnd.next() * size
        if abs(x - size / 2) < size * 0.34 and size * 0.10 < y < size * 0.90:
            continue
        if x < size * 0.06 or x > size * 0.94 or y < size * 0.05 or y > size * 0.95:
            continue
        r = size * 0.004 + rnd.next() * size * 0.0085
        a = 45 + int(rnd.next() * 95)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
        placed += 1
    return layer


def star(size, center, r, color=GOLD_BRIGHT):
    cx, cy = center
    poly = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.44
        poly.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(poly, fill=color + (255,))
    return layer


def tree(size, cx, top, bottom, width):
    """Three tidy tiers with a thin rim of snow along the branches."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    height = bottom - top
    trunk_w = width * 0.14
    d.rectangle(
        [cx - trunk_w / 2, bottom - height * 0.02, cx + trunk_w / 2, bottom + height * 0.08],
        fill=(104, 68, 38, 255),
    )
    tiers = 3
    for i in range(tiers):
        f1 = (i + 1) / tiers
        tier_top = top + height * (i / tiers) * 0.90
        tier_bottom = top + height * (0.34 + 0.66 * f1)
        tier_w = width * (0.50 + 0.50 * f1)
        body = lerp(PINE_LIGHT, PINE_DARK, i / (tiers - 1))
        d.polygon(
            [(cx, tier_top), (cx - tier_w / 2, tier_bottom), (cx + tier_w / 2, tier_bottom)],
            fill=SNOW + (255,),
        )
        # shift the green up a little: what is left below is the snow on the branches
        inset = max(size * 0.0045, (tier_bottom - tier_top) * 0.08)
        d.polygon(
            [
                (cx, tier_top + inset * 0.35),
                (cx - tier_w * 0.48, tier_bottom - inset),
                (cx + tier_w * 0.48, tier_bottom - inset),
            ],
            fill=body + (255,),
        )
    # red and gold baubles
    rnd = Rand(5)
    spots = [(-0.20, 0.55, GOLD), (0.22, 0.72, RED_LIGHT), (-0.05, 0.84, GOLD),
             (0.13, 0.93, GOLD), (-0.26, 0.88, RED_LIGHT)]
    for fx, fy, color in spots:
        bx = cx + fx * width
        by = top + height * fy
        r = width * 0.027
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=color + (240,))
    return layer


def santa_hat(canvas, center, width, angle=24):
    hat_w = width
    hat_h = width * 1.06
    pad = int(width * 1.8)
    size = pad * 2
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size / 2, size / 2

    brim_h = hat_h * 0.20
    brim = Image.new("L", (size, size), 0)
    ImageDraw.Draw(brim).rounded_rectangle(
        [cx - hat_w / 2, cy - brim_h / 2, cx + hat_w / 2, cy + brim_h / 2],
        radius=brim_h / 2, fill=255,
    )

    base_w = hat_w * 0.84
    tip = (cx + hat_w * 0.24, cy - hat_h * 0.95)
    left = bezier_pts((cx - base_w / 2, cy - brim_h * 0.1),
                      (cx - base_w * 0.40, cy - hat_h * 0.68), tip)
    right = bezier_pts((cx + base_w / 2, cy - brim_h * 0.1),
                       (cx + base_w * 0.34, cy - hat_h * 0.50), tip)
    cone = Image.new("L", (size, size), 0)
    ImageDraw.Draw(cone).polygon(left + right[::-1], fill=255)

    red = gradient_fill(cone, RED_LIGHT, RED_DARK)
    shade = Image.new("L", (size, size), 0)
    ImageDraw.Draw(shade).polygon(
        bezier_pts(tip, (cx + hat_w * 0.12, cy - hat_h * 0.30), (cx + hat_w * 0.18, cy)) + right[::-1],
        fill=80,
    )
    shade = shade.filter(ImageFilter.GaussianBlur(width * 0.06))
    red = Image.composite(Image.new("RGBA", (size, size), (70, 0, 14, 255)), red, shade)

    white = Image.new("RGBA", (size, size), (255, 252, 247, 255))
    pom_r = hat_w * 0.16
    pom = Image.new("L", (size, size), 0)
    ImageDraw.Draw(pom).ellipse([tip[0] - pom_r, tip[1] - pom_r, tip[0] + pom_r, tip[1] + pom_r],
                                fill=255)

    soft = Image.new("L", (size, size), 0)
    ImageDraw.Draw(soft).ellipse(
        [tip[0] - pom_r, tip[1] - pom_r * 0.7, tip[0] + pom_r, tip[1] + pom_r * 1.5], fill=60)
    soft = soft.filter(ImageFilter.GaussianBlur(width * 0.04))

    layer = alpha_over(layer, tinted(soft, (25, 0, 8)))
    layer = alpha_over(layer, masked(red, cone))
    layer = alpha_over(layer, masked(white, pom))
    layer = alpha_over(layer, masked(white, brim))

    layer = layer.rotate(angle, resample=Image.BICUBIC, center=(cx, cy))
    full = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    full.paste(layer, (int(center[0] - cx), int(center[1] - cy)), layer)
    return full


def bezier_pts(p0, p1, p2, steps=90):
    out = []
    for i in range(steps + 1):
        t = i / steps
        out.append((
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1],
        ))
    return out


def tinted(mask, color):
    out = Image.new("RGBA", mask.size, color + (255,))
    out.putalpha(mask)
    return out


def masked(img, mask):
    out = img.copy()
    out.putalpha(mask)
    return out


def alpha_over(base, top):
    return Image.alpha_composite(base, top)


def gradient_fill(mask, top, bottom):
    size = mask.size[0]
    grad = vertical_gradient(size, top, bottom).convert("RGBA")
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out


def fit_font(text, max_width, start):
    size = start
    while size > 10:
        f = ImageFont.truetype(FONT, size)
        box = f.getbbox(text)
        if box[2] - box[0] <= max_width:
            return f
        size -= 4
    return ImageFont.truetype(FONT, 10)


def draw_numbers(img, size, cy, width, scale=1.0):
    font = fit_font("2048", width, int(size * 0.40))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).text((size / 2, cy), "2048", font=font, fill=255, anchor="mm")
    shadow = mask.filter(ImageFilter.GaussianBlur(size * 0.010)).point(lambda v: int(v * 0.5))
    shadow = shadow.transform((size, size), Image.AFFINE, (1, 0, 0, 0, 1, -size * 0.006))
    img.alpha_composite(tinted(shadow, (0, 0, 0)))
    img.alpha_composite(gradient_fill(mask, CREAM, CREAM_DEEP))
    return font, mask


def artwork(size, with_numbers=True):
    """Tree, star, snow and the numerals."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    k = size / BASE

    layer.alpha_composite(tree(size, size / 2, TREE_TOP * k, TREE_BOTTOM * k, size * 0.315))
    layer.alpha_composite(star(size, (size / 2, STAR_CY * k), STAR_R * k))
    layer.alpha_composite(snow_dots(size))
    if with_numbers:
        draw_numbers(layer, size, NUM_CY * k, NUM_W * k)
    return layer


def full_icon():
    img = vertical_gradient(S, NIGHT_TOP, NIGHT_BOTTOM).convert("RGBA")

    glow = radial_alpha(S, (S * 0.5, -S * 0.08), S * 0.80, 165)
    img = Image.composite(Image.new("RGBA", (S, S), (58, 186, 128, 255)), img,
                          glow.point(lambda v: int(v * 0.55)))
    red = radial_alpha(S, (S * 1.03, S * 1.02), S * 0.66, 175)
    img = Image.composite(Image.new("RGBA", (S, S), (150, 26, 46, 255)), img,
                          red.point(lambda v: int(v * 0.62)))

    img.alpha_composite(artwork(S))

    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    inset = int(S * 0.052)
    ImageDraw.Draw(ring).rounded_rectangle(
        [inset, inset, S - inset, S - inset],
        radius=int(S * 0.19), outline=GOLD + (75,), width=max(2, int(S * 0.0045)),
    )
    img.alpha_composite(ring)
    img.putalpha(squircle(S))
    return img.resize((BASE, BASE), Image.LANCZOS)


def adaptive_foreground():
    """Transparent 432x432; art kept inside the 66% safe zone of the adaptive icon."""
    out = 432
    inner = int(out * 0.62)           # safe circle diameter (66%) minus a hair
    art = artwork(S, with_numbers=True)
    bbox = art.getbbox()
    art = art.crop(bbox)
    scale = inner / max(art.width, art.height)
    art = art.resize((max(1, int(art.width * scale)), max(1, int(art.height * scale))),
                     Image.LANCZOS)
    layer = Image.new("RGBA", (out, out), (0, 0, 0, 0))
    layer.paste(art, ((out - art.width) // 2, (out - art.height) // 2), art)
    return layer


def preview(master, path):
    sizes = [512, 144, 96, 64, 48]
    imgs = [master.resize((s, s), Image.LANCZOS) for s in sizes]
    pad = 18
    w = sum(i.width for i in imgs) + pad * (len(imgs) + 1)
    h = 512 + pad * 2
    sheet = Image.new("RGB", (w, h), (22, 22, 22))
    x = pad
    for im in imgs:
        sheet.paste(im, (x, pad + (512 - im.height) // 2), im)
        x += im.width + pad
    sheet.save(path)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    master = full_icon()
    master.save(os.path.join(outdir, "512.png"), optimize=True)
    master.save(os.path.join(outdir, "full_512.png"))
    adaptive_foreground().save(os.path.join(outdir, "foreground.png"), optimize=True)
    preview(master, os.path.join(outdir, "preview.png"))
    print("wrote", outdir)


if __name__ == "__main__":
    main()
