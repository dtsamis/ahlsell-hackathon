import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_FILES = [
    os.path.join(BASE_DIR, "STEEL-TEAM", "index.html"),
    os.path.join(BASE_DIR, "presentation", "index.html")
]

new_team_html = """      <!-- Team Members Row -->
      <div id="teamMembersContainer" class="flex flex-wrap items-center justify-center gap-6 pt-4 w-full">
        <!-- Member 1: Björn Bergström -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col items-center text-center w-64 shadow-xl hover:border-cyan-500/50 transition duration-300">
          <div class="w-28 h-28 rounded-full overflow-hidden border-2 border-cyan-400/80 shadow-lg shadow-cyan-500/20 mb-4 bg-slate-950 flex items-center justify-center">
            <img src="images/team/bjorn.png" alt="Björn Bergström" class="w-full h-full object-cover">
          </div>
          <h3 class="text-base font-bold text-white tracking-tight">Björn Bergström</h3>
          <p class="text-xs text-slate-400 font-mono mt-0.5">STEEL-TEAM</p>
          <a href="https://www.linkedin.com/in/bjorn-bergstrom/" target="_blank" rel="noopener noreferrer" class="mt-3.5 inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-950/70 border border-blue-800/80 text-blue-300 hover:bg-blue-600 hover:text-white text-[11px] font-mono transition">
            <i class="fa-brands fa-linkedin text-sm text-blue-400"></i>
            <span>linkedin.com/in/bjorn-bergstrom</span>
          </a>
        </div>

        <!-- Member 2: Arjith Chalasani -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col items-center text-center w-64 shadow-xl hover:border-cyan-500/50 transition duration-300">
          <div class="w-28 h-28 rounded-full overflow-hidden border-2 border-cyan-400/80 shadow-lg shadow-cyan-500/20 mb-4 bg-slate-950 flex items-center justify-center">
            <img src="images/team/arjith.jpg" alt="Arjith Chalasani" class="w-full h-full object-cover">
          </div>
          <h3 class="text-base font-bold text-white tracking-tight">Arjith Chalasani</h3>
          <p class="text-xs text-slate-400 font-mono mt-0.5">STEEL-TEAM</p>
          <a href="https://www.linkedin.com/in/arjithchalasani" target="_blank" rel="noopener noreferrer" class="mt-3.5 inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-950/70 border border-blue-800/80 text-blue-300 hover:bg-blue-600 hover:text-white text-[11px] font-mono transition">
            <i class="fa-brands fa-linkedin text-sm text-blue-400"></i>
            <span>linkedin.com/in/arjithchalasani</span>
          </a>
        </div>

        <!-- Member 3: Dimitrios Tsamis -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col items-center text-center w-64 shadow-xl hover:border-cyan-500/50 transition duration-300">
          <div class="w-28 h-28 rounded-full overflow-hidden border-2 border-cyan-400/80 shadow-lg shadow-cyan-500/20 mb-4 bg-slate-950 flex items-center justify-center">
            <img src="images/team/dimitrios.jpg" alt="Dimitrios Tsamis" class="w-full h-full object-cover">
          </div>
          <h3 class="text-base font-bold text-white tracking-tight">Dimitrios Tsamis</h3>
          <p class="text-xs text-slate-400 font-mono mt-0.5">STEEL-TEAM</p>
          <a href="https://www.linkedin.com/in/dimitriostsamis" target="_blank" rel="noopener noreferrer" class="mt-3.5 inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-950/70 border border-blue-800/80 text-blue-300 hover:bg-blue-600 hover:text-white text-[11px] font-mono transition">
            <i class="fa-brands fa-linkedin text-sm text-blue-400"></i>
            <span>linkedin.com/in/dimitriostsamis</span>
          </a>
        </div>
      </div>"""

for path in TARGET_FILES:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the team members container
    import re
    pattern = r'<div id="teamMembersContainer".*?</div>\s*</section>'
    replacement = new_team_html + "\n    </section>"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated", path)
