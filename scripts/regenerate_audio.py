import os
import asyncio
import edge_tts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEEL_AUDIO_DIR = os.path.join(BASE_DIR, "STEEL-TEAM", "audio")
PRES_AUDIO_DIR = os.path.join(BASE_DIR, "presentation", "audio")

os.makedirs(STEEL_AUDIO_DIR, exist_ok=True)
os.makedirs(PRES_AUDIO_DIR, exist_ok=True)

VOICE = "en-US-AndrewNeural"

SLIDE_SCRIPTS = {
    1: "Welcome. In technical wholesale distribution like Ahlsell, quotation speed wins deals, but data privacy is non-negotiable. Today, we present an automated backend that converts complex architectural blueprints directly into verified Bills of Materials in milliseconds—analyzed entirely locally with zero data ever leaving the premises.",
    2: "The industrial bottleneck today is manual estimation. Contractors submit sets of fifty to two hundred drawing sheets, and estimators spend twenty to forty-five minutes per page counting fixtures by hand. This creates a multi-day backlog, human miscounts on site, and lost bid conversions to competing suppliers.",
    3: "Our solution is Symbol Detector Version 1, powered by a lightweight YOLO eleven-s model with under ten million parameters. By scanning dense drawings at four hundred DPI in high-resolution tiles, the system captures microscopic details without downsampling. Crucially, the engine runs completely on-premise on standard hardware: zero external cloud dependencies, zero latency delays, and guaranteed data confidentiality for proprietary drawings.",
    4: "Here is the visual proof on a real Swedish school blueprint. On the left is the raw drawing, packed with dimensions, room labels, and hatching. In under one hundred milliseconds, our backend cuts through the clutter, cleanly extracting twenty-one distinct elements, including wash basins, classroom whiteboards, and repetitive corridor coat racks.",
    5: "Looking at the performance numbers: the model achieved ninety-five point two percent precision on this unseen test drawing, with one hundred percent recall on critical sanitary fixtures. It accurately captured all eleven coat hooks along corridor rows, with only one single false toilet that an estimator can dismiss in seconds.",
    6: "For Ahlsell, the business impact is clear. First, quote turnaround collapses from a full day to seconds, directly boosting contractor win rates. Second, generic blueprint symbols map straight into Ahlsell inventory SKUs. Third, verified visual audit trails drastically reduce job site misorders. And most importantly, complete on-premise security: confidential client blueprints and architect IP never leave your local servers, providing total data sovereignty.",
    7: "In summary, we have validated a high-speed, accurate backend that bridges architectural drawings directly into Ahlsell's commercial pipeline—rapid, precise, and completely secure on-premise.",
    8: "Thank you for your time and consideration. The STEEL-TEAM is now ready for your questions and discussion."
}

async def generate():
    for slide_num, text in SLIDE_SCRIPTS.items():
        steel_path = os.path.join(STEEL_AUDIO_DIR, f"slide{slide_num}.mp3")
        pres_path = os.path.join(PRES_AUDIO_DIR, f"slide{slide_num}.mp3")
        
        success = False
        for attempt in range(3):
            try:
                print(f"Generating audio for Slide {slide_num} (attempt {attempt + 1})...")
                comm = edge_tts.Communicate(text, VOICE)
                await comm.save(steel_path)
                with open(steel_path, "rb") as f_in, open(pres_path, "wb") as f_out:
                    f_out.write(f_in.read())
                print(f"Successfully saved Slide {slide_num}")
                success = True
                break
            except Exception as e:
                print(f"Retry {attempt+1} on Slide {slide_num} due to: {e}")
                await asyncio.sleep(2)
        if not success:
            raise RuntimeError(f"Failed to generate audio for slide {slide_num}")

if __name__ == "__main__":
    asyncio.run(generate())
