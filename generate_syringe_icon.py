from PIL import Image, ImageDraw, ImageFont

EMOJI = "💉"
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BG_COLOR = (15, 23, 42)
NATIVE_SIZE = 136  # NotoColorEmoji's native bitmap strike size

def make_icon(size, out_path):
    # Render at the font's native size first, since it's a fixed-size bitmap font
    canvas = Image.new("RGBA", (NATIVE_SIZE, NATIVE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT_PATH, size=NATIVE_SIZE)
    bbox = draw.textbbox((0, 0), EMOJI, font=font, embedded_color=True)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (NATIVE_SIZE - text_w) / 2 - bbox[0]
    y = (NATIVE_SIZE - text_h) / 2 - bbox[1]
    draw.text((x, y), EMOJI, font=font, embedded_color=True)

    # Composite onto a solid background at the final target size
    final = Image.new("RGBA", (size, size), BG_COLOR + (255,))
    scaled_emoji = canvas.resize((size, size), Image.LANCZOS)
    final.alpha_composite(scaled_emoji)
    final.convert("RGB").save(out_path, "PNG")
    print(f"wrote {out_path} ({size}x{size})")

make_icon(192, "/home/madfella/peptidetrack/static/icon-192.png")
make_icon(512, "/home/madfella/peptidetrack/static/icon-512.png")
