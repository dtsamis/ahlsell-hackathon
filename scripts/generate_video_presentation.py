import os
import sys
import asyncio
import subprocess
import edge_tts
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRES_DIR = os.path.join(BASE_DIR, "presentation")
AUDIO_DIR = os.path.join(PRES_DIR, "audio")
FRAMES_DIR = os.path.join(PRES_DIR, "frames")
OUTPUT_VIDEO = os.path.join(PRES_DIR, "Ahlsell_Symbol_Detector_Presentation.mp4")
FFMPEG = r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

VOICE = "en-US-AndrewNeural"

SLIDE_SCRIPTS = {
    1: "Welcome. In technical wholesale distribution like Ahlsell, quotation speed wins deals. Today, we present an automated backend that converts complex, unstructured architectural CAD blueprints directly into verified Bills of Materials in milliseconds.",
    2: "The industrial bottleneck today is manual estimation. Contractors submit sets of fifty to two hundred drawing sheets, and estimators spend twenty to forty-five minutes per page counting fixtures by hand. This creates a multi-day backlog, human miscounts on site, and lost bid conversions to competing suppliers.",
    3: "Our solution is Symbol Detector Version 1, powered by a lightweight YOLO eleven-s model with under ten million parameters. By scanning dense drawings at four hundred DPI in high-resolution tiles, the system captures microscopic details without downsampling. It is trained specifically on eight high-volume Ahlsell categories across sanitary plumbing and building hardware.",
    4: "Here is the visual proof on a real Swedish school blueprint. On the left is the raw drawing, packed with dimensions, room labels, and hatching. In under one hundred milliseconds, our backend cuts through the clutter, cleanly extracting twenty-one distinct elements, including wash basins, classroom whiteboards, and repetitive corridor coat racks.",
    5: "Looking at the performance numbers: the model achieved ninety-five point two percent precision on this unseen test drawing, with one hundred percent recall on critical sanitary fixtures. It accurately captured all eleven coat hooks along corridor rows, with only one single false toilet that an estimator can dismiss in seconds.",
    6: "For Ahlsell, the business impact is clear. First, quote turnaround collapses from days to seconds, directly boosting contractor win rates. Second, generic blueprint symbols map straight into Ahlsell inventory SKUs. And third, verified visual audit trails drastically reduce job site misorders and costly warehouse return freight.",
    7: "In summary, we have validated a high-speed, accurate backend that bridges architectural drawings directly into Ahlsell's commercial pipeline. Thank you, and we welcome your questions."
}


async def generate_all_audio():
    print("Generating speech audio tracks with edge-tts...")
    for slide_num, text in SLIDE_SCRIPTS.items():
        out_path = os.path.join(AUDIO_DIR, f"slide{slide_num}.mp3")
        print(f"  - Generating audio for Slide {slide_num}...")
        comm = edge_tts.Communicate(text, VOICE)
        await comm.save(out_path)
    print("All audio tracks generated successfully!")


def get_audio_duration(file_path):
    cmd = [
        FFMPEG, "-i", file_path, "-f", "null", "-"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, errors="ignore")
    # Parse Duration: 00:00:15.32
    import re
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        h, m_, s = m.groups()
        return int(h) * 3600 + int(m_) * 60 + float(s)
    return 15.0


def draw_header(draw, title, subtitle):
    # Badge
    draw.rectangle([80, 50, 420, 85], fill=(8, 47, 73), outline=(14, 116, 144), width=1)
    draw.text((95, 58), "AHLSELL HACKATHON · CAPABILITY TRACK", fill=(56, 189, 248))

    draw.text((80, 105), title, fill=(255, 255, 255))
    draw.text((80, 155), subtitle, fill=(148, 163, 184))


def render_slide_1(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)

    # Center hero badge
    draw.rectangle([710, 200, 1210, 245], fill=(8, 47, 73), outline=(14, 116, 144), width=2)
    draw.text((740, 212), "SYMBOL DETECTOR V1 · BACKEND CAPABILITY", fill=(56, 189, 248))

    draw.text((360, 310), "Instant Blueprint Takeoff for Ahlsell", fill=(255, 255, 255))
    draw.text((310, 400), "From Dense CAD Drawings to Verified Bills of Materials in Milliseconds", fill=(56, 189, 248))
    draw.text((450, 480), "Automating contractor quotation and inventory SKU matching across Nordic projects", fill=(148, 163, 184))

    # Metric Cards
    cards = [
        (">99%", "Takeoff Time Saved", (6, 182, 212), 260),
        ("95.2%", "Detection Precision", (16, 185, 129), 780),
        ("8 Classes", "Core Ahlsell Fixtures", (59, 130, 246), 1300),
    ]
    for val, lbl, col, x in cards:
        draw.rectangle([x, 620, x + 360, 770], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.text((x + 35, 645), val, fill=col)
        draw.text((x + 35, 715), lbl, fill=(203, 213, 225))

    draw.text((780, 950), "Presented by Dimitrios · Ahlsell Hackathon", fill=(100, 116, 139))
    img.save(path)


def render_slide_2(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "The Industrial Bottleneck: Manual Estimation Friction", "Why manual takeoff delays quotes and costs wholesale distributors deals")

    problems = [
        (80, "The Quotation Delay", "Contractors submit 50–200 blueprint sheets. Manual counting takes 20–45 mins per sheet, creating a 3–5 day lag on contractor RFQ turnaround.", (244, 63, 94), "3–5 Day RFQ Lag"),
        (680, "Human Fatigue & Miscounts", "Dense Swedish CAD drawings with leader lines and hatching cause missed items (e.g. tiny cloakroom hooks, valves, sanitary connections).", (245, 158, 11), "Site Shortages & Waste"),
        (1280, "Lost Bid Win-Rates", "In technical wholesale, contractors order from the supplier that quotes first. Taking days to assemble materials directly loses sales to competitors.", (6, 182, 212), "Lost Customer Orders"),
    ]

    for x, title, desc, col, tag in problems:
        draw.rectangle([x, 260, x + 560, 780], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.rectangle([x + 30, 300, x + 110, 380], fill=(col[0] // 4, col[1] // 4, col[2] // 4), outline=col, width=2)
        draw.text((x + 30, 420), title, fill=(255, 255, 255))

        # Wrap text
        words = desc.split()
        lines = []
        cur = []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 42:
                lines.append(" ".join(cur))
                cur = []
        if cur:
            lines.append(" ".join(cur))

        y = 480
        for line in lines:
            draw.text((x + 30, y), line, fill=(148, 163, 184))
            y += 32

        draw.rectangle([x + 30, 700, x + 530, 745], fill=(3, 7, 18), outline=(51, 65, 85))
        draw.text((x + 45, 712), tag, fill=col)

    img.save(path)


def render_slide_3(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "The Technology: Symbol Detector v1 (YOLO11s)", "High-resolution 400 DPI tiling engineered for dense architectural drawings")

    specs = [
        (80, "YOLO11s Architecture", "9.4M Parameters", "Lightweight COCO-pretrained backbone; fast inference on commodity hardware without heavy GPU clusters."),
        (530, "400 DPI Tiling", "1024×1024 px Tiles", "Cuts dense sheets into 1,707 tiles; preserves microscopic geometry like coat hooks and keyboxes without downsampling."),
        (980, "Real Training Data", "55 Deduplicated Sheets", "Trained on 4 production construction projects across 9,080 iterations; balanced oversampling of rare classes."),
        (1430, "Fast Training", "1.9 Hours on M4 Pro", "Rapid fine-tuning capability allows Ahlsell to roll out new trade symbol packs in hours."),
    ]

    for x, title, sub, desc in specs:
        draw.rectangle([x, 260, x + 410, 520], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.text((x + 25, 290), title, fill=(255, 255, 255))
        draw.text((x + 25, 330), sub, fill=(6, 182, 212))
        
        words = desc.split()
        lines = []
        cur = []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 32:
                lines.append(" ".join(cur))
                cur = []
        if cur:
            lines.append(" ".join(cur))
        y = 380
        for l in lines:
            draw.text((x + 25, y), l, fill=(148, 163, 184))
            y += 26

    # 8 Symbol Classes Banner
    draw.rectangle([80, 570, 1840, 840], fill=(15, 23, 42), outline=(14, 116, 144), width=2)
    draw.text((110, 600), "8 Targeted Ahlsell High-Frequency Symbol Classes:", fill=(255, 255, 255))
    draw.text((110, 635), "Calibrated on 17 validation sheets and tested on 16 held-out pages", fill=(148, 163, 184))

    classes = [
        ("wash basin", "VVS / Sanitary", (6, 182, 212), 110, 690),
        ("toilet", "VVS / Sanitary", (6, 182, 212), 520, 690),
        ("mirror", "Sanitary Fit-out", (6, 182, 212), 930, 690),
        ("hook", "Building Hardware", (168, 85, 247), 1340, 690),
        ("hat rack", "Building Hardware", (168, 85, 247), 110, 750),
        ("clothes rail", "Building Hardware", (168, 85, 247), 520, 750),
        ("whiteboard", "Commercial Interior", (14, 165, 233), 930, 750),
        ("post box", "Building Hardware", (16, 185, 129), 1340, 750),
    ]

    for name, domain, col, cx, cy in classes:
        draw.rectangle([cx, cy, cx + 380, cy + 46], fill=(3, 7, 18), outline=(30, 41, 59))
        draw.rectangle([cx + 12, cy + 18, cx + 22, cy + 28], fill=col)
        draw.text((cx + 32, cy + 12), name, fill=(255, 255, 255))
        draw.text((cx + 220, cy + 12), domain, fill=(100, 116, 139))

    img.save(path)


def render_slide_4(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Empirical Proof: Real-World Swedish School Blueprint", "Sheet A-40-2-A001: Automatic extraction of 21 discrete symbols in under 100 milliseconds")

    before_path = os.path.join(PRES_DIR, "images", "before.png")
    after_path = os.path.join(PRES_DIR, "images", "after.png")

    # Load and place images side by side
    b_img = Image.open(before_path)
    a_img = Image.open(after_path)

    # Frame 1: Before
    draw.rectangle([80, 240, 930, 960], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
    draw.text((105, 255), "Raw CAD Blueprint (Dense Noise & Text)", fill=(203, 213, 225))
    b_fit = b_img.resize((810, 640), Image.Resampling.LANCZOS)
    img.paste(b_fit, (100, 295))

    # Frame 2: After
    draw.rectangle([990, 240, 1840, 960], fill=(15, 23, 42), outline=(14, 116, 144), width=2)
    draw.text((1015, 255), "Symbol Detector v1 Output (21 Isolated Items)", fill=(56, 189, 248))
    a_fit = a_img.resize((810, 640), Image.Resampling.LANCZOS)
    img.paste(a_fit, (1010, 295))

    img.save(path)


def render_slide_5(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "Correctness & Accuracy Metrics", "Evaluated on unseen complex Swedish educational facility drawing")

    metrics = [
        (80, "Detection Precision", "95.2%", "20 True Positives out of 21 detections on zero-shot test drawing.", (16, 185, 129)),
        (530, "Sanitary Recall (VVS)", "100%", "Both wash basins (pantry & RWC) detected with zero misses.", (6, 182, 212)),
        (980, "Micro-Fixture Catch", "11 / 11", "All coat hooks in corridor racks captured without human counting.", (59, 130, 246)),
        (1430, "False Positives", "Only 1", "Only 1 false toilet detected; discarded in 5-second human review.", (245, 158, 11)),
    ]

    for x, lbl, val, desc, col in metrics:
        draw.rectangle([x, 250, x + 410, 450], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.text((x + 25, 275), lbl, fill=(148, 163, 184))
        draw.text((x + 25, 315), val, fill=col)
        draw.text((x + 25, 385), desc, fill=(203, 213, 225))

    # Table
    draw.rectangle([80, 490, 1840, 880], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
    draw.text((110, 520), "DETECTED SYMBOL", fill=(100, 116, 139))
    draw.text((450, 520), "AHLSELL DOMAIN", fill=(100, 116, 139))
    draw.text((820, 520), "EXTRACTED COUNT", fill=(100, 116, 139))
    draw.text((1200, 520), "CORRECTNESS", fill=(100, 116, 139))
    draw.text((1500, 520), "PRACTICAL VALUE", fill=(100, 116, 139))

    rows = [
        ("wash basin", "Sanitary / VVS", "2 units", "100% True Positive", "Pantry & RWC accessible washroom", 570),
        ("hook", "Building Hardware", "11 units", "100% True Positive", "Cloakroom & corridor racks", 630),
        ("whiteboard", "Commercial Interior", "7 units", "100% True Positive", "Classrooms, BILD, FOKUS spaces", 690),
        ("toilet", "Sanitary / VVS", "1 unit", "1 False Alarm", "Effortlessly dismissed in UI review", 750),
    ]

    for sym, dom, cnt, corr, val, y in rows:
        draw.line([(100, y - 10), (1820, y - 10)], fill=(30, 41, 59))
        draw.text((110, y), sym, fill=(255, 255, 255))
        draw.text((450, y), dom, fill=(56, 189, 248))
        draw.text((820, y), cnt, fill=(255, 255, 255))
        col_c = (16, 185, 129) if "True" in corr else (245, 158, 11)
        draw.text((1200, y), corr, fill=col_c)
        draw.text((1500, y), val, fill=(148, 163, 184))

    img.save(path)


def render_slide_6(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)
    draw_header(draw, "What Ahlsell Actually Gains: Commercial ROI", "Translating automated drawing takeoff into measurable wholesale margin")

    benefits = [
        (80, 260, "From 3 Days to 3 Seconds (Instant RFQ Quote)", "Speed wins contractor bids. In wholesale distribution, whoever returns the quote first captures the purchase order. Automated takeoff locks in bids while competitors are still counting.", (6, 182, 212)),
        (980, 260, "Direct Ahlsell Catalog SKU Mapping", "Generic CAD symbols translate automatically to Ahlsell inventory numbers (e.g. Gustavsberg basins, Geberit cisterns, mounting kits). Converts blueprints directly into high-margin Ahlsell carts.", (59, 130, 246)),
        (80, 560, "Reduced Return Logistics & Job Site Waste", "Every item has an auditable pixel bounding box and spatial record. Eliminates misordered quantities and expensive warehouse restocking freight when pallets are rejected on site.", (16, 185, 129)),
        (980, 560, "Empowered Human Estimators", "Estimators stop acting like manual counting machines. The model handles 95% of tedious detection, while estimators spend 30 seconds confirming candidates and focusing on deal closing.", (168, 85, 247)),
    ]

    for x, y, title, desc, col in benefits:
        draw.rectangle([x, y, x + 860, y + 250], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
        draw.rectangle([x + 25, y + 25, x + 65, y + 65], fill=col)
        draw.text((x + 85, y + 30), title, fill=(255, 255, 255))

        words = desc.split()
        lines = []
        cur = []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 60:
                lines.append(" ".join(cur))
                cur = []
        if cur:
            lines.append(" ".join(cur))
        ty = y + 85
        for l in lines:
            draw.text((x + 85, ty), l, fill=(148, 163, 184))
            ty += 28

    img.save(path)


def render_slide_7(path):
    img = Image.new("RGB", (1920, 1080), color=(3, 7, 18))
    draw = ImageDraw.Draw(img)

    draw.rectangle([860, 220, 1060, 320], fill=(8, 47, 73), outline=(14, 116, 144), width=3)
    draw.text((930, 255), "A", fill=(56, 189, 248))

    draw.text((490, 370), "Proven Backend Capability · Measurable Business Value", fill=(255, 255, 255))
    draw.text((430, 440), "Lightweight YOLO11s model running at sub-100ms latency with 95.2% empirical precision", fill=(148, 163, 184))

    # Summary Card
    draw.rectangle([360, 530, 1560, 780], fill=(15, 23, 42), outline=(30, 41, 59), width=2)
    
    bullets = [
        ("Fast & Deployable Everywhere:", "Compact 9.4M parameter model; low compute footprint ready for cloud or edge.", 570),
        ("High-Resolution 400 DPI Tiling:", "Pinpoints microscopic hardware fixtures without downsampling distortion.", 630),
        ("Clear Commercial ROI for Ahlsell:", "Accelerated quote win rates, direct SKU catalog integration, and reduced returns.", 690),
    ]

    for title, desc, y in bullets:
        draw.rectangle([400, y + 5, 412, y + 17], fill=(16, 185, 129))
        draw.text((430, y), title, fill=(255, 255, 255))
        draw.text((760, y), desc, fill=(148, 163, 184))

    draw.text((760, 870), "Thank you! Ready for questions and discussion.", fill=(56, 189, 248))
    img.save(path)


def render_all_slides():
    print("Rendering high-resolution 1080p slide frames...")
    render_slide_1(os.path.join(FRAMES_DIR, "slide1.png"))
    render_slide_2(os.path.join(FRAMES_DIR, "slide2.png"))
    render_slide_3(os.path.join(FRAMES_DIR, "slide3.png"))
    render_slide_4(os.path.join(FRAMES_DIR, "slide4.png"))
    render_slide_5(os.path.join(FRAMES_DIR, "slide5.png"))
    render_slide_6(os.path.join(FRAMES_DIR, "slide6.png"))
    render_slide_7(os.path.join(FRAMES_DIR, "slide7.png"))
    print("All 7 slide frames rendered successfully!")


def assemble_video():
    print("Assembling video presentation using FFmpeg...")
    concat_list_path = os.path.join(PRES_DIR, "concat_list.txt")
    part_videos = []

    for i in range(1, 8):
        frame = os.path.join(FRAMES_DIR, f"slide{i}.png")
        audio = os.path.join(AUDIO_DIR, f"slide{i}.mp3")
        duration = get_audio_duration(audio) + 1.0  # +1s buffer
        part_out = os.path.join(PRES_DIR, f"part{i}.mp4")

        cmd = [
            FFMPEG, "-y",
            "-loop", "1", "-i", frame,
            "-i", audio,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            part_out
        ]
        print(f"  - Rendering Slide {i} clip ({duration:.1f}s)...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        part_videos.append(part_out)

    with open(concat_list_path, "w", encoding="utf-8") as f:
        for p in part_videos:
            clean_p = p.replace("\\", "/")
            f.write(f"file '{clean_p}'\n")

    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        OUTPUT_VIDEO
    ]
    print("Concatenating into final MP4 video...")
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    print(f"SUCCESS: Video generated at {OUTPUT_VIDEO}")
    print(f"File size: {os.path.getsize(OUTPUT_VIDEO) / 1024 / 1024:.2f} MB")

    # Cleanup intermediate clips
    for p in part_videos:
        try: os.remove(p)
        except: pass
    try: os.remove(concat_list_path)
    except: pass


async def main():
    await generate_all_audio()
    render_all_slides()
    assemble_video()


if __name__ == "__main__":
    asyncio.run(main())
