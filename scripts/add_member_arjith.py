import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILES = [
    os.path.join(BASE_DIR, "STEEL-TEAM", "index.html"),
    os.path.join(BASE_DIR, "presentation", "index.html")
]

card_html = """        <!-- Member 2: Arjith Chalasani -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col items-center text-center w-56 shadow-xl hover:border-cyan-500/50 transition duration-300">
          <div class="w-28 h-28 rounded-full overflow-hidden border-2 border-cyan-400/80 shadow-lg shadow-cyan-500/20 mb-4 bg-slate-950 flex items-center justify-center">
            <img src="images/team/arjith.jpg" alt="Arjith Chalasani" class="w-full h-full object-cover">
          </div>
          <h3 class="text-base font-bold text-white tracking-tight">Arjith Chalasani</h3>
          <p class="text-xs text-slate-400 font-mono mt-0.5">STEEL-TEAM</p>
          <a href="https://www.linkedin.com/in/arjithchalasani" target="_blank" rel="noopener noreferrer" class="mt-3.5 inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-600/20 border border-blue-500/40 text-blue-300 hover:bg-blue-600 hover:text-white text-xs font-medium transition">
            <i class="fa-brands fa-linkedin text-sm"></i>
            <span>LinkedIn</span>
          </a>
        </div>"""

for path in TARGET_FILES:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    placeholder = "<!-- Team members will be populated here -->"
    if "Arjith Chalasani" not in content:
        content = content.replace(placeholder, card_html + "\n        " + placeholder)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated", path)
