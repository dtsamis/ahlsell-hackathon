import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILES = [
    os.path.join(BASE_DIR, "STEEL-TEAM", "index.html"),
    os.path.join(BASE_DIR, "presentation", "index.html")
]

for file_path in TARGET_FILES:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings
    content = content.replace("\r\n", "\n")

    # 1. Header total slides count
    content = content.replace('<span id="totalSlidesNum">7</span>', '<span id="totalSlidesNum">8</span>')

    # 2. Slide 6: Change 3 Days to 1 Day
    content = content.replace(
        '<h4 class="text-base font-bold text-white">From 3 Days to 3 Seconds: RFQ &rarr; Quote</h4>',
        '<h4 class="text-base font-bold text-white">From 1 Day to 3 Seconds: RFQ &rarr; Quote</h4>'
    )

    # 3. Slide 7: Remove thank you and questions part
    old_slide7_bottom = """      <div class="pt-2 text-sm text-cyan-400 font-semibold">
        Thank you! Ready for questions and discussion.
      </div>
    </section>"""
    new_slide7_bottom = """    </section>"""
    content = content.replace(old_slide7_bottom, new_slide7_bottom)

    # 4. Insert Slide 8 after Slide 7 (before </main>)
    slide8_html = """    <!-- SLIDE 8: Thank You & Team -->
    <section class="slide flex-col items-center justify-center text-center max-w-5xl space-y-8 w-full" data-slide="8">
      <div class="space-y-3">
        <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono font-medium shadow-lg">
          <i class="fa-solid fa-users"></i>
          <span>Ahlsell Hackathon · STEEL-TEAM</span>
        </div>
        <h2 class="text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
          Thank You!
        </h2>
        <p class="text-base text-slate-400 max-w-xl mx-auto">
          We are ready for your questions and discussion.
        </p>
      </div>

      <!-- Team Members Row -->
      <div id="teamMembersContainer" class="flex flex-wrap items-center justify-center gap-6 pt-4 w-full">
        <!-- Team members will be populated here -->
      </div>
    </section>
  </main>"""

    if 'data-slide="8"' not in content:
        content = content.replace('  </main>', slide8_html)

    # 5. Total slides in JavaScript
    content = content.replace("const totalSlides = 7;", "const totalSlides = 8;")

    # 6. Speaker notes in JavaScript
    old_notes_end = """      6: "For Ahlsell, the business impact is clear. First, quote turnaround collapses from days to seconds, directly boosting contractor win rates. Second, generic blueprint symbols map straight into Ahlsell inventory SKUs. Third, verified visual audit trails drastically reduce job site misorders. And most importantly, complete on-premise security: confidential client blueprints and architect IP never leave your local servers, providing total data sovereignty.",
      7: "In summary, we have validated a high-speed, accurate backend that bridges architectural drawings directly into Ahlsell's commercial pipeline—rapid, precise, and completely secure on-premise. Thank you, and we welcome your questions."
    };"""

    new_notes_end = """      6: "For Ahlsell, the business impact is clear. First, quote turnaround collapses from a full day to seconds, directly boosting contractor win rates. Second, generic blueprint symbols map straight into Ahlsell inventory SKUs. Third, verified visual audit trails drastically reduce job site misorders. And most importantly, complete on-premise security: confidential client blueprints and architect IP never leave your local servers, providing total data sovereignty.",
      7: "In summary, we have validated a high-speed, accurate backend that bridges architectural drawings directly into Ahlsell's commercial pipeline—rapid, precise, and completely secure on-premise.",
      8: "Thank you for your time and consideration. The STEEL-TEAM is now ready for your questions and discussion."
    };"""

    content = content.replace(old_notes_end, new_notes_end)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file_path}")
