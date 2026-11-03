import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILES = [
    os.path.join(BASE_DIR, "STEEL-TEAM", "index.html"),
    os.path.join(BASE_DIR, "presentation", "index.html")
]

for file_path in TARGET_FILES:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Slide 1 Badge
    old_badge = """      <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono font-medium shadow-lg">
        <i class="fa-solid fa-microchip"></i>
        <span>Symbol Detector v1 · High-Speed Backend Engine</span>
      </div>"""
    new_badge = """      <div class="flex flex-wrap items-center justify-center gap-2">
        <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono font-medium shadow-lg">
          <i class="fa-solid fa-microchip"></i>
          <span>Symbol Detector v1 · High-Speed Engine</span>
        </div>
        <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-emerald-950/90 border border-emerald-600/80 text-emerald-300 text-xs font-mono font-bold shadow-lg">
          <i class="fa-solid fa-shield-halved"></i>
          <span>100% On-Premise · Zero Data Leaves Premises</span>
        </div>
      </div>"""

    # 2. Slide 1 Metrics Grid
    old_grid = """      <div class="pt-6 grid grid-cols-3 gap-6 max-w-xl mx-auto text-left">
        <div class="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div class="text-2xl font-bold text-cyan-400 font-mono">>99%</div>
          <div class="text-xs text-slate-400 mt-1">Takeoff Time Saved</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div class="text-2xl font-bold text-emerald-400 font-mono">95.2%</div>
          <div class="text-xs text-slate-400 mt-1">Detection Precision</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div class="text-2xl font-bold text-blue-400 font-mono">8 Classes</div>
          <div class="text-xs text-slate-400 mt-1">Core Ahlsell Fixtures</div>
        </div>
      </div>"""
    new_grid = """      <div class="pt-6 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto text-left">
        <div class="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div class="text-2xl font-bold text-cyan-400 font-mono">>99%</div>
          <div class="text-xs text-slate-400 mt-1">Takeoff Time Saved</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div class="text-2xl font-bold text-emerald-400 font-mono">95.2%</div>
          <div class="text-xs text-slate-400 mt-1">Detection Precision</div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div class="text-2xl font-bold text-blue-400 font-mono">8 Classes</div>
          <div class="text-xs text-slate-400 mt-1">Core Ahlsell Fixtures</div>
        </div>
        <div class="bg-slate-900/60 border border-emerald-800/80 p-4 rounded-xl bg-emerald-950/20">
          <div class="text-2xl font-bold text-emerald-400 font-mono">100% Local</div>
          <div class="text-xs text-slate-400 mt-1">Zero Cloud Leakage</div>
        </div>
      </div>"""

    # 3. Slide 3 Banner
    old_spec_end = """        <div class="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div class="text-[11px] text-slate-400 font-mono uppercase">Training Time</div>
          <div class="text-lg font-bold text-white mt-1">1.9 Hours</div>
          <div class="text-xs text-cyan-400 font-mono mt-1">Fast Iteration Cycle</div>
          <p class="text-[10px] text-slate-400 mt-2">Trained on an M4 Pro GPU; low compute footprint.</p>
        </div>
      </div>"""
    new_spec_end = """        <div class="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div class="text-[11px] text-slate-400 font-mono uppercase">Training Time</div>
          <div class="text-lg font-bold text-white mt-1">1.9 Hours</div>
          <div class="text-xs text-cyan-400 font-mono mt-1">Fast Iteration Cycle</div>
          <p class="text-[10px] text-slate-400 mt-2">Trained on an M4 Pro GPU; low compute footprint.</p>
        </div>
      </div>

      <!-- Air-Gapped Local Privacy Banner -->
      <div class="bg-gradient-to-r from-emerald-950/80 via-slate-900/90 to-cyan-950/80 border border-emerald-500/50 rounded-xl p-3.5 flex items-center space-x-3.5 shadow-lg">
        <div class="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-xl flex-shrink-0">
          <i class="fa-solid fa-shield-halved"></i>
        </div>
        <div class="text-xs">
          <div class="font-bold text-emerald-300 uppercase tracking-wide text-[11px] flex items-center gap-1.5">
            <span>Critical Security Advantage: 100% On-Premise Execution</span>
            <span class="bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded text-[9px] font-mono">Zero Cloud Upload</span>
          </div>
          <div class="text-slate-300 mt-0.5 leading-relaxed">
            All CAD blueprints are parsed and inferred locally on Ahlsell internal infrastructure. Proprietary customer drawings, tender plans, and intellectual property <strong>never leave the building</strong>.
          </div>
        </div>
      </div>"""

    # 4. Slide 6 Benefit 4
    old_b4 = """        <!-- Benefit 4 -->
        <div class="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl flex items-start space-x-4">
          <div class="w-10 h-10 rounded-xl bg-purple-950 border border-purple-800 text-purple-400 flex items-center justify-center flex-shrink-0 text-lg">
            <i class="fa-solid fa-user-check"></i>
          </div>
          <div>
            <h4 class="text-base font-bold text-white">Empowered Human Estimators</h4>
            <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Estimators no longer start from a blank page. The model handles 95% of tedious detection, while estimators spend 30 seconds confirming candidates (e.g. dismissing 1 false toilet with 1 click).
            </p>
          </div>
        </div>"""
    new_b4 = """        <!-- Benefit 4: 100% Local Privacy & Air-Gapped Security -->
        <div class="bg-slate-900/70 border border-emerald-800/70 p-5 rounded-2xl flex items-start space-x-4 bg-gradient-to-br from-slate-900/90 to-emerald-950/30">
          <div class="w-10 h-10 rounded-xl bg-emerald-950 border border-emerald-700 text-emerald-400 flex items-center justify-center flex-shrink-0 text-lg">
            <i class="fa-solid fa-lock"></i>
          </div>
          <div>
            <h4 class="text-base font-bold text-emerald-300">100% Local Analysis · Zero Data Leaves Premises</h4>
            <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Confidential commercial tenders and client architectural IP stay strictly behind Ahlsell's firewall. Zero third-party cloud API dependencies, zero vendor lock-in, and full GDPR & enterprise compliance.
            </p>
          </div>
        </div>"""

    # 5. Slide 7 Bullet
    old_s7_bullet = """        <div class="flex items-center space-x-2 text-slate-200">
          <i class="fa-solid fa-circle-check text-cyan-400"></i>
          <span><strong>Fast & Scalable:</strong> Pure ONNX Runtime execution ready for high-concurrency cloud or edge.</span>
        </div>"""
    new_s7_bullet = """        <div class="flex items-center space-x-2 text-slate-200">
          <i class="fa-solid fa-circle-check text-emerald-400"></i>
          <span><strong>100% On-Premise:</strong> Zero cloud upload. Sensitive client drawings never leave Ahlsell's premises.</span>
        </div>
        <div class="flex items-center space-x-2 text-slate-200">
          <i class="fa-solid fa-circle-check text-cyan-400"></i>
          <span><strong>Fast & Scalable:</strong> Pure ONNX Runtime execution running in sub-100ms on local hardware.</span>
        </div>"""

    # 6. Speaker Notes
    old_notes = """    const speakerNotes = {
      1: "Hook: Ahlsell is in the business of supplying construction products, but the biggest bottleneck to winning sales is the days it takes to manually count materials from drawings. Today we present an automated backend that turns blueprints into structured material lists in milliseconds.",
      2: "Problem: Contractors submit stacks of 50-200 blueprint sheets. Manual takeoff is slow (20-45 minutes per sheet) and prone to human error. In B2B distribution, whoever quotes first wins the order. Right now, manual estimation delays cost Ahlsell deals.",
      3: "Tech Specs: Keep it high-level. We trained a compact 9.4M parameter YOLO11s model—Symbol Detector v1—specifically targeting 8 high-volume Ahlsell items (toilets, wash basins, mirrors, coat hooks, hat racks, clothes rails, whiteboards, post boxes). We cut dense 400 DPI blueprints into high-res tiles so microscopic items like coat hooks are never missed. It trained in under 2 hours on an M4 Pro GPU and runs in ~80ms at inference.",
      4: "Visual Proof: Walk the judges through sheet A-40-2-A001 from a real Swedish school. On the left is the raw input—cluttered with dimensions and Swedish room tags. On the right is our backend output: in less than a tenth of a second, the model extracted 21 distinct fixtures with pixel-precise bounding boxes.",
      5: "Honest Metrics: The model scored 95.2% precision (20 out of 21 detections were spot on). It achieved 100% recall on the high-value plumbing fixtures—both wash basins were found. It also caught all 11 cloakroom hooks. Out of 21 items, only one single false toilet occurred—which an estimator dismisses with one click in the review UI.",
      6: "Business ROI: First, speed to quote drops from days to seconds—speed wins bids. Second, these generic CAD symbols map straight into Ahlsell SKUs, turning a PDF into an orderable cart. Third, exact visual coordinates drastically reduce wrong shipments and costly warehouse returns.",
      7: "Closing: We've validated that the backend works reliably on real Swedish construction drawings. The model is lightweight, fast, accurate, and directly ties blueprints to Ahlsell's commercial bottom line. Thank you, and we welcome your questions!"
    };"""

    new_notes = """    const speakerNotes = {
      1: "Welcome. In technical wholesale distribution like Ahlsell, quotation speed wins deals, but data privacy is non-negotiable. Today, we present an automated backend that converts complex architectural blueprints directly into verified Bills of Materials in milliseconds—analyzed entirely locally with zero data ever leaving the premises.",
      2: "The industrial bottleneck today is manual estimation. Contractors submit sets of fifty to two hundred drawing sheets, and estimators spend twenty to forty-five minutes per page counting fixtures by hand. This creates a multi-day backlog, human miscounts on site, and lost bid conversions to competing suppliers.",
      3: "Our solution is Symbol Detector Version 1, powered by a lightweight YOLO eleven-s model with under ten million parameters. By scanning dense drawings at four hundred DPI in high-resolution tiles, the system captures microscopic details without downsampling. Crucially, the engine runs completely on-premise on standard hardware: zero external cloud dependencies, zero latency delays, and guaranteed data confidentiality for proprietary drawings.",
      4: "Here is the visual proof on a real Swedish school blueprint. On the left is the raw drawing, packed with dimensions, room labels, and hatching. In under one hundred milliseconds, our backend cuts through the clutter, cleanly extracting twenty-one distinct elements, including wash basins, classroom whiteboards, and repetitive corridor coat racks.",
      5: "Looking at the performance numbers: the model achieved ninety-five point two percent precision on this unseen test drawing, with one hundred percent recall on critical sanitary fixtures. It accurately captured all eleven coat hooks along corridor rows, with only one single false toilet that an estimator can dismiss in seconds.",
      6: "For Ahlsell, the business impact is clear. First, quote turnaround collapses from days to seconds, directly boosting contractor win rates. Second, generic blueprint symbols map straight into Ahlsell inventory SKUs. Third, verified visual audit trails drastically reduce job site misorders. And most importantly, complete on-premise security: confidential client blueprints and architect IP never leave your local servers, providing total data sovereignty.",
      7: "In summary, we have validated a high-speed, accurate backend that bridges architectural drawings directly into Ahlsell's commercial pipeline—rapid, precise, and completely secure on-premise. Thank you, and we welcome your questions."
    };"""

    # Normalize line endings for replacement
    content = content.replace("\r\n", "\n")
    content = content.replace(old_badge.replace("\r\n", "\n"), new_badge)
    content = content.replace(old_grid.replace("\r\n", "\n"), new_grid)
    content = content.replace(old_spec_end.replace("\r\n", "\n"), new_spec_end)
    content = content.replace(old_b4.replace("\r\n", "\n"), new_b4)
    content = content.replace(old_s7_bullet.replace("\r\n", "\n"), new_s7_bullet)
    content = content.replace(old_notes.replace("\r\n", "\n"), new_notes)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file_path}")
