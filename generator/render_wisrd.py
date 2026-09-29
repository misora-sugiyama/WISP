

"""WISP worksheet renderer (legacy task IDs retained).

Generates input worksheets, ground-truth images, reference images, answer masks,
and JSONL metadata for the WISRD layout and V0--V7 information conditions.
"""



import argparse

import json

import math

import os

import random

import string

import time

from pathlib import Path

from typing import Any, Dict, List, Optional, Tuple



import numpy as np

from PIL import Image, ImageDraw, ImageFont, ImageChops





def ts():

    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())









VARIANTS = [



    dict(var_id="V0", name="prompt_only",        image_text=False, prompt_mode="strong_task",   refs_mode="none"),

    dict(var_id="V1", name="prompt+text",        image_text=True,  prompt_mode="strong_task",   refs_mode="none"),

    dict(var_id="V2", name="text_only",          image_text=True,  prompt_mode="generic_weak",  refs_mode="none"),

    dict(var_id="V3", name="minimal",            image_text=False, prompt_mode="generic_min",   refs_mode="none"),

    dict(var_id="V4", name="prompt_only+refs",   image_text=False, prompt_mode="strong_task",   refs_mode="style+icl"),

    dict(var_id="V5", name="text+refs",          image_text=True,  prompt_mode="strong_task",   refs_mode="style+icl"),

    dict(var_id="V6", name="minimal+refs",       image_text=False, prompt_mode="generic_min",   refs_mode="style+icl"),

    dict(var_id="V7", name="text_only+refs",     image_text=True,  prompt_mode="generic_weak",  refs_mode="style+icl"),

]



VARIANT_MAP = {v["var_id"]: v for v in VARIANTS}





W, H = 1024, 1024

SCALE = 4

W2, H2 = W*SCALE, H*SCALE



HEADER_H = 200

HEADER_H2 = HEADER_H*SCALE



FRAME_SIZE = 760

FRAME_SIZE2 = FRAME_SIZE*SCALE

FRAME_LEFT  = (W - FRAME_SIZE)//2

FRAME_TOP   = HEADER_H + 20

FRAME_LEFT2 = FRAME_LEFT*SCALE

FRAME_TOP2  = FRAME_TOP*SCALE





WHITE = (255,255,255)

BLACK = (0,0,0)

GRAY_TEXT  = (170,170,170)

GRAY_FRAME = (180,180,180)

DARK_GRAY  = (80,80,80)

LIGHT_GRAY = (170,170,170)

RED   = (230,0,0)

BLUE  = (0,90,255)





LW_FRAME = 6*SCALE

LW_BLACK = 8*SCALE

LW_GRAY  = 8*SCALE

DOT_R    = 10*SCALE





def find_font():
    explicit = os.environ.get("WISP_FONT_PATH")
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"WISP_FONT_PATH does not exist: {path}")
        return str(path)
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf"),
    ]
    for path in candidates:
        if Path(path).is_file():
            return path
    raise FileNotFoundError("Set WISP_FONT_PATH to a TrueType font file. See docs/DATA.md.")


FONT_PATH = find_font()


def load_font(size_px: int):
    return ImageFont.truetype(FONT_PATH, size=size_px)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int):

    words = text.split()

    lines = []

    cur = ""

    for w in words:

        cand = (cur + " " + w).strip()

        if draw.textlength(cand, font=font) <= max_w or not cur:

            cur = cand

        else:

            lines.append(cur)

            cur = w

    if cur:

        lines.append(cur)

    return lines



def fit_text_in_box(draw: ImageDraw.ImageDraw, text: str, box_w: int, box_h: int, max_font: int, min_font: int=14):



    for fs in range(max_font, min_font-1, -2):

        font = load_font(fs)

        lines = wrap_text(draw, text, font, box_w)



        ascent, descent = font.getmetrics()

        line_h = ascent + descent + int(fs*0.25)

        total_h = line_h * len(lines)

        if total_h <= box_h:

            return font, lines, line_h

    font = load_font(min_font)

    lines = wrap_text(draw, text, font, box_w)

    ascent, descent = font.getmetrics()

    line_h = ascent + descent + int(min_font*0.25)

    return font, lines, line_h



def render_base_canvas():

    img = Image.new("RGB", (W2, H2), WHITE)

    draw = ImageDraw.Draw(img)



    x0,y0 = FRAME_LEFT2, FRAME_TOP2

    x1,y1 = x0+FRAME_SIZE2, y0+FRAME_SIZE2

    draw.rectangle([x0,y0,x1,y1], outline=GRAY_FRAME, width=LW_FRAME)

    return img, draw, (x0,y0,x1,y1)



def draw_header_text(img: Image.Image, text: str):

    draw = ImageDraw.Draw(img)

    margin = 60*SCALE

    box = (margin, 20*SCALE, W2-margin, HEADER_H2-10*SCALE)

    bw = box[2]-box[0]

    bh = box[3]-box[1]

    font, lines, line_h = fit_text_in_box(draw, text, bw, bh, max_font=40*SCALE, min_font=16*SCALE)

    y = box[1]

    for ln in lines:

        draw.text((box[0], y), ln, fill=GRAY_TEXT, font=font)

        y += line_h

    return img



def downsample(img2x: Image.Image):

    return img2x.resize((W,H), resample=Image.LANCZOS)

















CONSTRAINTS_COMMON = (

    "Keep all existing black lines and any printed text unchanged. "

    "Do not add any new lines, shapes, or marks other than the required edits."

)



def _join(*parts: str) -> str:

    return " ".join([p.strip() for p in parts if isinstance(p, str) and p.strip()])





TASK_CONTEXT: Dict[str, str] = {

    "fill_target_shape": "You are given an outlined target shape inside a light gray square frame.",

    "fill_and_center": "You are given an outlined target shape inside a light gray square frame.",

    "line_midpoint_mark": "You are given a black line segment inside a light gray square frame.",

    "line_intersections": "You are given black line segments inside a light gray square frame.",

    "two_circles": "You are given two black circles inside a light gray square frame.",

    "color_two_shapes": (

        "You are given two outlined shapes inside a light gray square frame. "

        "One outline is dark gray and the other outline is light gray."

    ),

    "circled_letter_base": "You are given a row of letters and exactly one letter is circled.",

    "circled_letter_allA": "You are given a row of letters and exactly one letter is circled.",

    "circled_letter_copy_single": "You are given a single circled letter.",

    "circled_letter_blank": "You are given a row of letters and exactly one position is circled.",

    "circled_letter_blankcircle": "You are given a row of letters and exactly one position is circled.",

    "count_dots_digit": "You are given black dots inside a light gray square frame.",

    "overlapping_shapes": "You are given multiple overlapping outlined shapes inside a light gray square frame.",

    "nested_squares": "You are given a nested squares pattern and an empty answer box.",

    "angle_copy": "You are given an angle and an empty answer box.",

    "amida": "You are given an amidakuji ladder diagram inside a light gray square frame.",

    "line_intersections_count": "You are given black line segments inside a light gray square frame.",

    "count_dots_visual": "You are given black dots inside a light gray square frame.",

}



TASK_INSTRUCTION: Dict[str, str] = {

    "fill_target_shape": "Fill the outlined target shape solid red.",

    "fill_and_center": "Fill the outlined target shape solid red and then place a small blue dot at the center of the filled shape.",

    "line_midpoint_mark": "Place a small red dot at the midpoint of the line segment.",

    "line_intersections": "Place a small red dot at every intersection point of the black lines.",

    "two_circles": "Place small red dots at both intersection points of the two circles.",

    "color_two_shapes": "Fill the dark gray outline shape solid red and fill the light gray outline shape solid blue.",

    "circled_letter_base": "Copy the circled letter into the answer box below using red ink.",

    "circled_letter_allA": "Copy the circled letter into the answer box below using red ink.",

    "circled_letter_copy_single": "Copy the circled letter into the answer box below using red ink.",

    "circled_letter_blankcircle": "Copy the circled letter into the answer box below using red ink. If the circled position is blank, leave the answer box below completely blank.",

    "circled_letter_blank": "Leave the answer box below completely blank and do not draw anything.",

    "count_dots_digit": "Count the dots and write the correct digit from 1 to 9 in the answer box below using red ink.",

    "overlapping_shapes": "Mark the center of every shape with a small red dot.",

    "nested_squares": "Copy the nested squares into the answer box using red outline lines with no fill.",

    "angle_copy": "Copy the angle into the answer box using red lines.",

    "amida": (

        "Start from the marked start at the top, follow the path down according to the horizontal rungs, "

        "and mark the final endpoint at the bottom with a small red dot."

    ),

    "line_intersections_count": "Count the intersection points of the black lines and write the number as a single digit in the answer box below using red ink.",

    "count_dots_visual": "Draw a thin red circle around each black dot.",

}





TASK_STRONG_EXTRA: Dict[str, str] = {

    "count_dots_visual": "Do not circle empty space and do not miss any dot.",

}





PROMPT_STRONG: Dict[str, str] = {

    task: _join(

        TASK_CONTEXT[task],

        TASK_INSTRUCTION[task],

        TASK_STRONG_EXTRA.get(task, ""),

        CONSTRAINTS_COMMON,

    )

    for task in TASK_CONTEXT.keys()

}



PROMPT_WEAK: Dict[str, str] = {

    task: _join(

        TASK_CONTEXT[task],

        TASK_INSTRUCTION[task],

    )

    for task in TASK_CONTEXT.keys()

}





GENERIC_WEAK = "Edit the image by following the written instructions that appear inside the image."

GENERIC_MIN  = "Edit the image."



def build_prompt(task: str, var_cfg: Dict[str, Any]) -> str:

    pm = var_cfg.get("prompt_mode", "strong_task")

    if pm == "strong_task":

        return PROMPT_STRONG[task]

    if pm == "weak_task":

        return PROMPT_WEAK[task]

    if pm == "generic_weak":

        return GENERIC_WEAK

    if pm == "generic_min":

        return GENERIC_MIN

    raise ValueError(f"Unknown prompt_mode {pm}")









def rand_rng(seed: int):

    return random.Random(seed)



def draw_answer_box(draw: ImageDraw.ImageDraw, frame: Tuple[int,int,int,int], label: str="ANSWER BOX", box_size: int=320):

    """Draw an answer box inside the gray frame (2x coordinates).

    Keep a small margin so the answer box never touches or overlaps the outer frame.
    """

    x0, y0, x1, y1 = frame

    bs = box_size * SCALE





    bx0 = (x0 + x1 - bs) // 2

    by0 = y0 + int(0.58 * (y1 - y0))

    bx1 = bx0 + bs

    by1 = by0 + bs





    margin = 24 * SCALE

    if by1 > y1 - margin:

        by1 = y1 - margin

        by0 = by1 - bs

    if by0 < y0 + margin:

        by0 = y0 + margin

        by1 = by0 + bs





    bx0 = max(bx0, x0 + margin)

    bx0 = min(bx0, x1 - margin - bs)

    bx1 = bx0 + bs



    draw.rectangle([bx0, by0, bx1, by1], outline=GRAY_FRAME, width=LW_FRAME)





    font = load_font(22 * SCALE)

    draw.text((bx0, by0 - 30 * SCALE), label, fill=GRAY_TEXT, font=font)

    return (bx0, by0, bx1, by1)





def put_centered_text(draw: ImageDraw.ImageDraw, box: Tuple[int,int,int,int], text: str, color=(230,0,0), font_size=120):

    x0,y0,x1,y1 = box

    fs = font_size*SCALE

    font = load_font(fs)

    w = draw.textlength(text, font=font)

    ascent, descent = font.getmetrics()

    h = ascent+descent

    cx = (x0+x1)//2

    cy = (y0+y1)//2

    draw.text((cx - w/2, cy - h/2), text, fill=color, font=font)



def mask_color(img: Image.Image, color: Tuple[int,int,int], thr=40):

    arr = np.array(img)

    c = np.array(color)[None,None,:]

    dist = np.sqrt(((arr - c)**2).sum(axis=2))

    return (dist < thr).astype(np.uint8)



def composite_side_by_side(imgL: Image.Image, imgR: Image.Image, gap=20):

    imgL = imgL.convert("RGB")

    imgR = imgR.convert("RGB")

    w = imgL.width + imgR.width + gap

    h = max(imgL.height, imgR.height)

    out = Image.new("RGB", (w,h), (255,255,255))

    out.paste(imgL, (0,0))

    out.paste(imgR, (imgL.width+gap,0))

    return out



def gen_fill_target_shape(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame





    shape = rng.choice(["circle", "square", "triangle"])





    sz = rng.randint(140, 260) * SCALE





    margin = 80 * SCALE

    max_allowed = int(0.45 * min(x1-x0, y1-y0) - margin)

    if max_allowed > 20 * SCALE:

        sz = min(sz, max_allowed)



    cx = rng.randint(x0 + sz + margin, x1 - sz - margin)

    cy = rng.randint(y0 + sz + margin, y1 - sz - margin)



    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)



    if shape == "circle":

        r = [cx-sz, cy-sz, cx+sz, cy+sz]

        draw.ellipse(r, outline=BLACK, width=LW_BLACK)

        dgt.ellipse(r, outline=BLACK, width=LW_BLACK, fill=RED)

        return base2x, gt2x, dict(shape=shape, bbox=[int(v) for v in r], center=(int(cx), int(cy)))



    if shape == "square":

        r = [cx-sz, cy-sz, cx+sz, cy+sz]

        draw.rectangle(r, outline=BLACK, width=LW_BLACK)

        dgt.rectangle(r, outline=BLACK, width=LW_BLACK, fill=RED)

        return base2x, gt2x, dict(shape=shape, bbox=[int(v) for v in r], center=(int(cx), int(cy)))





    th = rng.random() * 2 * math.pi

    pts = []

    for k in range(3):

        a = th + 2 * math.pi * k / 3.0

        pts.append((cx + int(math.cos(a) * sz), cy + int(math.sin(a) * sz)))





    draw.line([*pts[0], *pts[1]], fill=BLACK, width=LW_BLACK)

    draw.line([*pts[1], *pts[2]], fill=BLACK, width=LW_BLACK)

    draw.line([*pts[2], *pts[0]], fill=BLACK, width=LW_BLACK)





    dgt.polygon(pts, fill=RED)

    dgt.line([*pts[0], *pts[1]], fill=BLACK, width=LW_BLACK)

    dgt.line([*pts[1], *pts[2]], fill=BLACK, width=LW_BLACK)

    dgt.line([*pts[2], *pts[0]], fill=BLACK, width=LW_BLACK)



    return base2x, gt2x, dict(shape=shape, points=[(int(x), int(y)) for (x,y) in pts], center=(int(cx), int(cy)))

def gen_fill_and_center(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame

    cx = (x0+x1)//2 + rng.randint(-70,70)*SCALE

    cy = (y0+y1)//2 + rng.randint(-70,70)*SCALE

    sz = rng.randint(170,220)*SCALE

    r = [cx-sz, cy-sz, cx+sz, cy+sz]

    draw.rectangle(r, outline=BLACK, width=LW_BLACK)

    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    dgt.rectangle(r, outline=BLACK, width=LW_BLACK, fill=RED)



    dgt.ellipse([cx-DOT_R, cy-DOT_R, cx+DOT_R, cy+DOT_R], fill=BLUE)

    return base2x, gt2x, dict(center=(cx,cy))



def gen_line_midpoint_mark(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame

    pad = 120*SCALE

    ax = rng.randint(x0+pad, x1-pad)

    ay = rng.randint(y0+pad, y1-pad)

    bx = rng.randint(x0+pad, x1-pad)

    by = rng.randint(y0+pad, y1-pad)

    draw.line([ax,ay,bx,by], fill=BLACK, width=LW_BLACK)

    mx = (ax+bx)//2

    my = (ay+by)//2

    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    dgt.ellipse([mx-DOT_R, my-DOT_R, mx+DOT_R, my+DOT_R], fill=RED)

    return base2x, gt2x, dict(mid=(mx,my))



def gen_line_intersections(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame



    cx = (x0+x1)//2 + rng.randint(-40,40)*SCALE

    cy = (y0+y1)//2 + rng.randint(-40,40)*SCALE

    L = int(0.45*(x1-x0))



    th = rng.random()*math.pi

    dx = int(math.cos(th)*L)

    dy = int(math.sin(th)*L)



    p1 = (cx-dx, cy-dy)

    p2 = (cx+dx, cy+dy)



    th2 = th + math.pi/2 + (rng.random()-0.5)*0.2

    dx2 = int(math.cos(th2)*L)

    dy2 = int(math.sin(th2)*L)

    q1 = (cx-dx2, cy-dy2)

    q2 = (cx+dx2, cy+dy2)

    draw.line([*p1,*p2], fill=BLACK, width=LW_BLACK)

    draw.line([*q1,*q2], fill=BLACK, width=LW_BLACK)



    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    dgt.ellipse([cx-DOT_R, cy-DOT_R, cx+DOT_R, cy+DOT_R], fill=RED)

    return base2x, gt2x, dict(inters=[(cx,cy)])



def circle_intersections(c0, c1, r):



    (x0,y0),(x1,y1) = c0,c1

    dx = x1-x0

    dy = y1-y0

    d = math.hypot(dx,dy)

    if d<=1e-6 or d>=2*r:

        return []

    a = d/2

    h = math.sqrt(max(r*r - a*a, 0))

    xm = x0 + dx*0.5

    ym = y0 + dy*0.5



    ux = -dy/d

    uy = dx/d

    p3 = (xm + ux*h, ym + uy*h)

    p4 = (xm - ux*h, ym - uy*h)

    return [p3, p4]



def gen_two_circles(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame



    r = rng.randint(140,170)*SCALE

    cx = (x0+x1)//2

    cy = (y0+y1)//2



    d = rng.randint(int(0.9*r), int(1.5*r))



    c0 = (cx - d//2, cy)

    c1 = (cx + d//2, cy)



    draw.ellipse([c0[0]-r,c0[1]-r,c0[0]+r,c0[1]+r], outline=BLACK, width=LW_BLACK)

    draw.ellipse([c1[0]-r,c1[1]-r,c1[0]+r,c1[1]+r], outline=BLACK, width=LW_BLACK)



    pts = circle_intersections(c0,c1,r)

    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    inters=[]

    for (px,py) in pts:

        px=int(round(px)); py=int(round(py))

        inters.append((px,py))

        dgt.ellipse([px-DOT_R, py-DOT_R, px+DOT_R, py+DOT_R], fill=RED)

    return base2x, gt2x, dict(inters=inters, r=r, c0=c0, c1=c1)



def gen_color_two_shapes(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame



    cy = (y0+y1)//2 + rng.randint(-50,50)*SCALE

    cxL = (x0+x1)//2 - 170*SCALE

    cxR = (x0+x1)//2 + 170*SCALE

    sz = rng.randint(120,160)*SCALE



    if rng.random()<0.5:

        dark_shape = ("circle", [cxL-sz, cy-sz, cxL+sz, cy+sz])

        light_shape = ("rect", [cxR-sz, cy-sz, cxR+sz, cy+sz])

    else:

        dark_shape = ("rect", [cxL-sz, cy-sz, cxL+sz, cy+sz])

        light_shape = ("circle", [cxR-sz, cy-sz, cxR+sz, cy+sz])



    if dark_shape[0]=="circle": draw.ellipse(dark_shape[1], outline=DARK_GRAY, width=LW_GRAY)

    else: draw.rectangle(dark_shape[1], outline=DARK_GRAY, width=LW_GRAY)

    if light_shape[0]=="circle": draw.ellipse(light_shape[1], outline=LIGHT_GRAY, width=LW_GRAY)

    else: draw.rectangle(light_shape[1], outline=LIGHT_GRAY, width=LW_GRAY)



    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    if dark_shape[0]=="circle": dgt.ellipse(dark_shape[1], outline=DARK_GRAY, width=LW_GRAY, fill=RED)

    else: dgt.rectangle(dark_shape[1], outline=DARK_GRAY, width=LW_GRAY, fill=RED)

    if light_shape[0]=="circle": dgt.ellipse(light_shape[1], outline=LIGHT_GRAY, width=LW_GRAY, fill=BLUE)

    else: dgt.rectangle(light_shape[1], outline=LIGHT_GRAY, width=LW_GRAY, fill=BLUE)

    return base2x, gt2x, dict()



def gen_circled_letter_base(idx: int, seed: int=0, variant: str="base"):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame



    letters = []

    if variant=="allA":

        letters = ["A"]*8

    else:

        letters = rng.sample(list(string.ascii_uppercase), 8)

    circ_i = rng.randrange(8)



    if variant in ["blank","blankcircle"]:

        letters[circ_i] = ""



    single = (variant=="copy_single")

    if single:

        letters = [letters[circ_i]]

        circ_i = 0



    font = load_font(60*SCALE)



    if single:

        xs = [(x0+x1)//2]

    else:

        xs = np.linspace(x0+90*SCALE, x1-90*SCALE, len(letters)).astype(int).tolist()

    y_letters = y0 + 170*SCALE



    for i,ch in enumerate(letters):

        if ch=="":

            continue

        w = draw.textlength(ch, font=font)

        draw.text((xs[i]-w/2, y_letters), ch, fill=BLACK, font=font)



    cx = xs[circ_i]

    cy = y_letters + 40*SCALE

    r  = 52*SCALE

    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=GRAY_FRAME, width=LW_FRAME)





    abox = draw_answer_box(draw, frame, label="ANSWER BOX (draw letter)", box_size=320)





    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    target_letter = letters[circ_i] if not single else letters[0]

    if variant in ["blank","blankcircle"]:



        pass

    else:

        put_centered_text(dgt, abox, target_letter, color=RED, font_size=170)



    meta = dict(target_letter=target_letter, circ_i=circ_i, letters=letters, variant=variant, answer_box=abox)

    return base2x, gt2x, meta





def gen_circled_letter_blank_instruction(idx: int, seed: int=0):

    """Circled-letter control: the correct output is to leave the answer box blank (no red)."""

    base2x, _gt2x, meta = gen_circled_letter_base(idx, seed=seed, variant="base")

    gt2x = base2x.copy()

    meta2 = dict(meta)

    meta2["variant"] = "blank_instruction"

    return base2x, gt2x, meta2



def gen_count_dots_digit(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame





    abox = draw_answer_box(draw, frame, label="ANSWER BOX (write digit)", box_size=300)





    n = rng.randint(1,9)

    rr = DOT_R



    region = (

        x0 + 120*SCALE + rr,

        y0 + 120*SCALE + rr,

        x1 - 120*SCALE - rr,

        abox[1] - 60*SCALE - rr,

    )





    min_gap = 6 * SCALE

    min_dist = 2*rr + min_gap

    centers = []

    max_attempts = 5000



    for _ in range(n):

        placed = False

        px = region[0]

        py = region[1]

        for _a in range(max_attempts):

            px = rng.randint(region[0], region[2])

            py = rng.randint(region[1], region[3])

            if all((px-cx)**2 + (py-cy)**2 >= (min_dist**2) for (cx,cy) in centers):

                centers.append((px,py))

                placed = True

                break

        if not placed:



            min_dist = max(2*rr + 2*SCALE, int(min_dist * 0.9))

            for _a in range(max_attempts):

                px = rng.randint(region[0], region[2])

                py = rng.randint(region[1], region[3])

                if all((px-cx)**2 + (py-cy)**2 >= (min_dist**2) for (cx,cy) in centers):

                    centers.append((px,py))

                    placed = True

                    break

        if not placed:



            centers.append((px,py))



    dots = []

    for (px,py) in centers:

        draw.ellipse([px-rr, py-rr, px+rr, py+rr], fill=BLACK)

        dots.append(dict(cx=int(px), cy=int(py), r=int(rr)))





    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    put_centered_text(dgt, abox, str(n), color=RED, font_size=170)



    meta = dict(

        n_dots=int(n),

        gt_digit=int(n),

        answer_box_2x=abox,

        answer_box_1x=tuple(int(round(v/SCALE)) for v in abox),

        dots=dots,

        dot_r_2x=int(rr),

        min_dist_2x=int(min_dist),

    )

    return base2x, gt2x, meta



def gen_overlapping_shapes(idx: int, seed: int = 0):

    """Overlapping shapes (localization):
    Draw multiple overlapping congruent shapes, and the ground-truth is to mark
    the center of EVERY shape with a small RED dot.
    """

    rng = rand_rng(seed + idx)

    base2x, draw, frame = render_base_canvas()

    x0, y0, x1, y1 = frame





    kind = rng.choice(["circle", "square", "triangle"])





    n_rows = 2

    n_cols = rng.choice([3, 4])





    if n_cols == 4:

        r0 = rng.randint(70, 90)

    else:

        r0 = rng.randint(90, 120)

    r = r0 * SCALE





    spacing0 = int(r0 * rng.uniform(1.25, 1.55))

    spacing = spacing0 * SCALE



    cluster_w = (n_cols - 1) * spacing + 2 * r

    cluster_h = (n_rows - 1) * spacing + 2 * r



    margin = 60 * SCALE

    cx_frame = (x0 + x1) // 2

    cy_frame = (y0 + y1) // 2





    cluster_x0 = cx_frame - cluster_w // 2 + rng.randint(-60 * SCALE, 60 * SCALE)

    cluster_y0 = cy_frame - cluster_h // 2 + rng.randint(-120 * SCALE, 60 * SCALE)





    cluster_x0 = max(x0 + margin, min(cluster_x0, x1 - margin - cluster_w))

    cluster_y0 = max(y0 + margin, min(cluster_y0, y1 - margin - cluster_h))



    centers: List[Tuple[int, int]] = []

    jitter = int(0.12 * r)

    for rr in range(n_rows):

        for cc in range(n_cols):

            cx = cluster_x0 + r + cc * spacing + rng.randint(-jitter, jitter)

            cy = cluster_y0 + r + rr * spacing + rng.randint(-jitter, jitter)





            cx = max(x0 + margin + r, min(cx, x1 - margin - r))

            cy = max(y0 + margin + r, min(cy, y1 - margin - r))

            centers.append((int(cx), int(cy)))





    for (cx, cy) in centers:

        if kind == "circle":

            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLACK, width=LW_BLACK)



        elif kind == "square":

            draw.rectangle([cx - r, cy - r, cx + r, cy + r], outline=BLACK, width=LW_BLACK)



        else:



            th = rng.random() * 2 * math.pi

            pts = []

            for k in range(3):

                a = th + 2 * math.pi * k / 3.0

                pts.append((cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)))

            draw.line([*pts[0], *pts[1]], fill=BLACK, width=LW_BLACK)

            draw.line([*pts[1], *pts[2]], fill=BLACK, width=LW_BLACK)

            draw.line([*pts[2], *pts[0]], fill=BLACK, width=LW_BLACK)





    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    for (cx, cy) in centers:

        dgt.ellipse([cx - DOT_R, cy - DOT_R, cx + DOT_R, cy + DOT_R], fill=RED)



    meta = dict(kind=kind, r=int(r), centers=centers)

    return base2x, gt2x, meta

def gen_nested_squares(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame



    pad = 70*SCALE

    midx = (x0+x1)//2



    px0,py0,px1,py1 = (x0+pad, y0+pad, midx-pad, y1-pad)



    abox = (midx+pad, y0+pad, x1-pad, y1-pad)

    draw.rectangle(abox, outline=GRAY_FRAME, width=LW_FRAME)

    font = load_font(22*SCALE)

    draw.text((abox[0], abox[1]-30*SCALE), "ANSWER BOX", fill=GRAY_TEXT, font=font)





    levels = 3

    for i in range(levels):

        m = i*40*SCALE

        draw.rectangle([px0+m,py0+m,px1-m,py1-m], outline=BLACK, width=LW_BLACK)





    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    for i in range(levels):

        m = i*40*SCALE

        dgt.rectangle([abox[0]+m, abox[1]+m, abox[2]-m, abox[3]-m], outline=RED, width=LW_BLACK)

    return base2x, gt2x, dict(answer_box=abox)



def gen_angle_copy(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame

    pad = 70*SCALE

    midx = (x0+x1)//2



    ax0,ay0,ax1,ay1 = (x0+pad, y0+pad, midx-pad, y1-pad)

    cx = (ax0+ax1)//2

    cy = (ay0+ay1)//2

    L = int(0.35*(ax1-ax0))

    th1 = rng.random()*math.pi

    th2 = th1 + (0.4+0.4*rng.random())*math.pi

    p1=(cx+int(math.cos(th1)*L), cy+int(math.sin(th1)*L))

    p2=(cx+int(math.cos(th2)*L), cy+int(math.sin(th2)*L))

    draw.line([cx,cy,p1[0],p1[1]], fill=BLACK, width=LW_BLACK)

    draw.line([cx,cy,p2[0],p2[1]], fill=BLACK, width=LW_BLACK)



    abox = (midx+pad, y0+pad, x1-pad, y1-pad)

    draw.rectangle(abox, outline=GRAY_FRAME, width=LW_FRAME)

    font = load_font(22*SCALE)

    draw.text((abox[0], abox[1]-30*SCALE), "ANSWER BOX", fill=GRAY_TEXT, font=font)



    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    cx2=(abox[0]+abox[2])//2

    cy2=(abox[1]+abox[3])//2

    dgt.line([cx2,cy2,cx2+int(math.cos(th1)*L), cy2+int(math.sin(th1)*L)], fill=RED, width=LW_BLACK)

    dgt.line([cx2,cy2,cx2+int(math.cos(th2)*L), cy2+int(math.sin(th2)*L)], fill=RED, width=LW_BLACK)

    return base2x, gt2x, dict(answer_box=abox)



def gen_amida(idx: int, seed: int=0):

    rng = rand_rng(seed+idx)

    base2x, draw, frame = render_base_canvas()

    x0,y0,x1,y1 = frame

    n_cols = 5

    xs = np.linspace(x0+120*SCALE, x1-120*SCALE, n_cols).astype(int).tolist()

    top = y0+120*SCALE

    bot = y1-120*SCALE



    for x in xs:

        draw.line([x, top, x, bot], fill=BLACK, width=LW_BLACK)



    rungs=[]

    for i in range(n_cols-1):

        for _ in range(2):

            y = rng.randint(top+80*SCALE, bot-80*SCALE)

            rungs.append((i,y))

    rungs.sort(key=lambda t:t[1])

    for i,y in rungs:

        draw.line([xs[i], y, xs[i+1], y], fill=BLACK, width=LW_BLACK)



    start_col = rng.randrange(n_cols)



    sx = xs[start_col]; sy = top-40*SCALE

    draw.ellipse([sx-DOT_R, sy-DOT_R, sx+DOT_R, sy+DOT_R], fill=BLUE)





    col = start_col

    ycur = top

    for i,y in rungs:

        if y < ycur:

            continue



        if i==col:

            col = col+1; ycur = y

        elif i==col-1:

            col = col-1; ycur = y

    end_col = col

    ex = xs[end_col]; ey = bot+40*SCALE



    gt2x = base2x.copy()

    dgt = ImageDraw.Draw(gt2x)

    dgt.ellipse([ex-DOT_R, ey-DOT_R, ex+DOT_R, ey+DOT_R], fill=RED)

    meta=dict(start_col=start_col, end_col=end_col, end=(ex,ey))

    return base2x, gt2x, meta









def gen_count_dots_visual(idx, seed=12345):

    """Count-dots (visual): input has black dots; GT circles EACH dot with a thin RED ring.

    - Keep dot size uniform
    - Ensure dots do not overlap (and rings also do not overlap too much)
    - No answer box (answer is the circles around dots)
    """

    base2x, draw_base, frame = render_base_canvas()

    gt2x, draw_gt, _ = render_base_canvas()



    x0, y0, x1, y1 = frame

    fw = x1 - x0 + 1

    fh = y1 - y0 + 1



    rng = random.Random(seed * 100000 + idx + 321)



    n = rng.randint(1, 9)





    rr = 10 * SCALE



    ring_r = 14 * SCALE





    pad = 60 * SCALE

    rx0 = x0 + pad

    ry0 = y0 + pad

    rx1 = x1 - pad

    ry1 = y0 + int(0.45 * fh)



    min_dist = 3 * rr



    dots = []

    for _ in range(8000):

        if len(dots) >= n:

            break

        cx = rng.randint(rx0, rx1)

        cy = rng.randint(ry0, ry1)



        ok = True

        for (px, py) in dots:

            if (cx - px) ** 2 + (cy - py) ** 2 < (min_dist ** 2):

                ok = False

                break

        if ok:

            dots.append((cx, cy))





    for (cx, cy) in dots:

        draw_base.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=BLACK)

        draw_gt.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=BLACK)

        draw_gt.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], outline=RED, width=LW_RED_RING)



    meta = {

        "n": int(n),

        "dots": [{"cx": int(cx), "cy": int(cy), "r": int(rr), "ring_r": int(ring_r)} for (cx, cy) in dots],

    }

    return base2x, gt2x, meta



GEN_FNS = {

    "fill_target_shape": gen_fill_target_shape,

    "fill_and_center": gen_fill_and_center,

    "line_midpoint_mark": gen_line_midpoint_mark,

    "line_intersections": gen_line_intersections,

    "two_circles": gen_two_circles,

    "color_two_shapes": gen_color_two_shapes,

    "circled_letter_base": lambda idx, seed=0: gen_circled_letter_base(idx, seed=seed, variant="base"),

    "circled_letter_allA": lambda idx, seed=0: gen_circled_letter_base(idx, seed=seed, variant="allA"),

    "circled_letter_blank": gen_circled_letter_blank_instruction,

    "circled_letter_blankcircle": lambda idx, seed=0: gen_circled_letter_base(idx, seed=seed, variant="blankcircle"),

    "circled_letter_copy_single": lambda idx, seed=0: gen_circled_letter_base(idx, seed=seed, variant="copy_single"),

    "count_dots_digit": gen_count_dots_digit,

    "count_dots_visual": gen_count_dots_visual,

    "nested_squares": gen_nested_squares,

    "angle_copy": gen_angle_copy,

    "amida": gen_amida,

}





GEN_FNS["overlapping_shapes"] = gen_overlapping_shapes











LW_RED_RING = 5 * SCALE



CORE_TASKS = [

    "line_intersections",

    "line_midpoint_mark",

    "fill_target_shape",

    "circled_letter_base",

    "circled_letter_allA",

    "circled_letter_blank",

    "circled_letter_blankcircle",

    "circled_letter_copy_single",

    "count_dots_digit",

    "count_dots_visual",

    "overlapping_shapes",

]


# Public release guard: the reported benchmark interface exposes only the 11
# core WISRD worksheet tasks. Some helper functions above are retained for
# development, but they are not registered or reachable through the default
# generator interface.
_CORE_TASK_SET = set(CORE_TASKS)
TASK_CONTEXT = {k: v for k, v in TASK_CONTEXT.items() if k in _CORE_TASK_SET}
TASK_INSTRUCTION = {k: v for k, v in TASK_INSTRUCTION.items() if k in _CORE_TASK_SET}
GEN_FNS = {k: v for k, v in GEN_FNS.items() if k in _CORE_TASK_SET}





def save_img(img_highres: Image.Image, path: Path, header_text: Optional[str] = None) -> None:

    if header_text:

        img_highres = img_highres.copy()

        draw_header_text(img_highres, header_text)

    path.parent.mkdir(parents=True, exist_ok=True)

    downsample(img_highres).save(path)





def ensure_refs_for_task(task: str, sample_input: Image.Image, sample_gt: Image.Image, refs_dir: Path) -> List[str]:

    refs_dir.mkdir(parents=True, exist_ok=True)

    style_path = refs_dir / f"style_ref_{task}.png"

    if not style_path.exists():

        downsample(sample_gt).save(style_path)

    icl_path = refs_dir / f"icl_{task}.png"

    if not icl_path.exists():

        panel = composite_side_by_side(downsample(sample_input), downsample(sample_gt), gap=30)

        panel.save(icl_path)

    return [str(style_path.name if False else style_path), str(icl_path.name if False else icl_path)]





def generate_dataset(out_dir: Path, n_per_task: int = 2, seed: int = 12345, tasks: Optional[List[str]] = None, variants: Optional[List[str]] = None) -> Path:

    if n_per_task < 1:
        raise ValueError("n_per_task must be positive")

    if (out_dir / "items.jsonl").exists():
        raise FileExistsError("Choose a fresh output directory to keep generated datasets separate")

    tasks = tasks or CORE_TASKS

    variants = variants or [v["var_id"] for v in VARIANTS]

    if len(set(tasks)) != len(tasks) or len(set(variants)) != len(variants):
        raise ValueError("Tasks and variants must be unique")

    variant_rows = [VARIANT_MAP[v] for v in variants]



    dataset_dir = out_dir / "dataset"

    gt_dir = out_dir / "ground_truth"

    refs_dir = out_dir / "references"

    masks_dir = out_dir / "masks"

    for d in [dataset_dir, gt_dir, refs_dir, masks_dir]:

        d.mkdir(parents=True, exist_ok=True)



    def relpath(path: Path) -> str:

        try:

            return str(path.relative_to(out_dir))

        except ValueError:

            return str(path)



    items = []

    refs_map: Dict[str, List[str]] = {}

    for task in tasks:

        if task not in GEN_FNS:

            raise KeyError(f"Unknown task: {task}")

        for idx in range(n_per_task):

            base_img, gt_img, meta = GEN_FNS[task](idx, seed=seed)

            if idx == 0:

                refs_map[task] = [relpath(Path(p)) for p in ensure_refs_for_task(task, base_img, gt_img, refs_dir)]

            base_id = f"{task}_{idx:04d}"

            base_in = dataset_dir / f"{base_id}__notext.png"

            base_tx = dataset_dir / f"{base_id}__withtext.png"

            gt_path = gt_dir / f"{base_id}__gt.png"

            save_img(base_img, base_in, header_text=None)

            save_img(base_img, base_tx, header_text=PROMPT_STRONG[task])

            save_img(gt_img, gt_path, header_text=None)
            # Binary reference answer mask; the frozen scorer computes its own red mask.
            gt_rgb = np.asarray(Image.open(gt_path).convert("RGB")).astype(np.int16)
            r, g, b = gt_rgb[:, :, 0], gt_rgb[:, :, 1], gt_rgb[:, :, 2]
            red = (r > 150) & (g < 130) & (b < 130) & ((r - g) > 35) & ((r - b) > 35)
            mask_path = masks_dir / f"{base_id}__answer_mask.png"
            Image.fromarray((red * 255).astype(np.uint8)).save(mask_path)

            for var_cfg in variant_rows:

                var_id = var_cfg["var_id"]

                input_path = base_tx if var_cfg["image_text"] else base_in

                ref_paths = refs_map.get(task) if var_cfg["refs_mode"] == "style+icl" else None

                items.append({

                    "id": f"{base_id}__{var_id}",

                    "base_id": base_id,

                    "task": task,

                    "idx": idx,

                    "var_id": var_id,

                    "input_path": relpath(input_path),

                    "gt_path": relpath(gt_path),

                    "answer_mask_path": relpath(mask_path),

                    "prompt": build_prompt(task, var_cfg),

                    "ref_paths": ref_paths,

                    "meta": meta,

                })



    items_path = out_dir / "items.jsonl"

    with items_path.open("w", encoding="utf-8") as f:

        for row in items:

            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    (out_dir / "refs_map.json").write_text(json.dumps(refs_map, indent=2), encoding="utf-8")

    (out_dir / "generation_config.json").write_text(json.dumps({

        "created_utc": ts(),

        "font_file": Path(FONT_PATH).name,

        "purpose": "development samples; not a replacement for the frozen paper subset",

        "canvas": [W, H],

        "scale": SCALE,

        "frame_left_top_size": [FRAME_LEFT, FRAME_TOP, FRAME_SIZE],

        "n_per_task": n_per_task,

        "seed": seed,

        "tasks": tasks,

        "variants": variants,

    }, indent=2), encoding="utf-8")

    return items_path





def parse_args():

    p = argparse.ArgumentParser(description="Generate WISP development samples; use frozen data for paper reproduction.")

    p.add_argument("--out", type=Path, required=True, help="Output directory")

    p.add_argument("--n-per-task", type=int, default=2)

    p.add_argument("--seed", type=int, default=12345)

    p.add_argument("--tasks", nargs="*", default=None, help="Task IDs; default all core tasks")

    p.add_argument("--variants", nargs="*", default=None, help="Variant IDs; default V0--V7")

    return p.parse_args()





def main():

    args = parse_args()

    path = generate_dataset(args.out, n_per_task=args.n_per_task, seed=args.seed, tasks=args.tasks, variants=args.variants)

    print(f"saved {path}")





if __name__ == "__main__":

    main()
