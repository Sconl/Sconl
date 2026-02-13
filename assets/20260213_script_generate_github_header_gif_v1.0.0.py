#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import math

# Fix for Pylance "Import 'numpy' could not be resolved"
try:
    import numpy as np
except ImportError:
    np = None  # Pylance sees this import; runtime will fail if numpy missing

# === CONFIGURATION ===
WIDTH, HEIGHT = 1200, 200
TEXT_LINES = [
    "Decision Systems Architect.",
    "Privacy First Infrastructure Engineer.",
    "Design. Decide. Deploy."
]
FONT_PATH = "Poppins-Bold.ttf"  # Replace with your local Poppins-Bold.ttf
FONT_SIZE = 60
GRADIENT_START = (0, 200, 0)      # green
GRADIENT_END = (180, 255, 0)      # lime
CHAR_DELAY = 0.1                   # seconds per character
FADE_DURATION = 0.3                # fade in/out for typing effect
PAUSE_BETWEEN_LINES = 1.0          # seconds pause after each sentence
FPS = 24

# === HELPERS ===
def linear_gradient(color1, color2, width):
    if width <= 1:
        return [tuple(color1)]
    return [
        tuple(int(color1[i] + (color2[i]-color1[i])*x/(width-1)) for i in range(3))
        for x in range(width)
    ]

def ease_in_out(t):
    """Smooth easing function (0->1)"""
    t = max(0.0, min(1.0, t))
    return 3*t**2 - 2*t**3

def render_text_line(text, upto=None):
    """Render text up to `upto` characters (for typing effect)."""
    if upto is None or upto > len(text):
        upto = len(text)
    text_to_render = text[:upto]

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Measure using textbbox
    temp_img = Image.new("RGBA", (10, 10))
    temp_draw = ImageDraw.Draw(temp_img)

    bbox = temp_draw.textbbox((0, 0), text_to_render, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    img = Image.new("RGBA", (width or 1, height or 1), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Create gradient
    grad = linear_gradient(GRADIENT_START, GRADIENT_END, width)
    grad_img = Image.new("RGBA", (width, height))
    grad_draw = ImageDraw.Draw(grad_img)
    for x in range(width):
        grad_draw.line([(x,0),(x,height)], fill=grad[x])

    # Mask for text
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((-bbox[0], -bbox[1]), text_to_render, font=font, fill=255)

    # Paste gradient with mask
    img.paste(grad_img, (0,0), mask)

    return img

# === PREPARE FRAMES ===
line_durations = [len(line)*CHAR_DELAY + FADE_DURATION + PAUSE_BETWEEN_LINES for line in TEXT_LINES]
total_duration = sum(line_durations)
num_frames = int(math.ceil(total_duration * FPS))

def make_frame(t):
    """Return a PIL.Image RGBA for time t (seconds)."""
    elapsed = 0.0
    for idx, line in enumerate(TEXT_LINES):
        line_duration = line_durations[idx]
        if elapsed <= t < elapsed + line_duration:
            line_idx = idx
            local_t = t - elapsed
            break
        elapsed += line_duration
    else:
        line_idx = len(TEXT_LINES) - 1
        local_t = line_durations[-1]

    # Determine how many characters to show
    chars_to_show = min(len(TEXT_LINES[line_idx]), int(local_t / CHAR_DELAY) + 1)
    line_img = render_text_line(TEXT_LINES[line_idx], upto=chars_to_show)

    # Apply fade-in and fade-out
    alpha = 1.0
    if local_t < FADE_DURATION:
        alpha = ease_in_out(local_t / FADE_DURATION)
    elif local_t > line_durations[line_idx] - FADE_DURATION:
        alpha = ease_in_out((line_durations[line_idx] - local_t) / FADE_DURATION)

    arr = np.array(line_img)
    arr = arr.astype(np.float32)
    arr[:,:,3] = arr[:,:,3] * alpha
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    line_img = Image.fromarray(arr, mode="RGBA")

    # Paste left-aligned so typing expands to the right
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    left_margin = 20
    x = left_margin
    y = (HEIGHT - line_img.height)//2
    img.paste(line_img, (x,y), line_img)
    return img

def pil_frames_from_make_frame():
    frames = []
    for i in range(num_frames):
        t = i / FPS
        frames.append(make_frame(t))
    return frames

def save_frames_as_gif(frames, out_path, fps=24):
    duration_ms = int(1000 / fps)
    first, rest = frames[0], frames[1:]
    first.save(
        out_path,
        save_all=True,
        append_images=rest,
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=True,
    )

# === MAIN ===
if __name__ == "__main__":
    print(f"Rendering {num_frames} frames ({total_duration:.2f}s at {FPS} FPS)...")
    frames = pil_frames_from_make_frame()
    out_name = "20260213_asset_animated_text_github_header_sconl.gif"
    save_frames_as_gif(frames, out_name, fps=FPS)
    print(f"Saved {out_name}")
