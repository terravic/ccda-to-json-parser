"""
HTML / Canvas Visualizer Generator for Parsed C-CDA JSON Documents.
Renders an executive interactive patient dashboard for Antigravity, Gemini Enterprise App,
Spark Canvas UI, or standalone browser viewing.
"""

import json
from typing import Any, Dict


def generate_patient_dashboard_html(data: Dict[str, Any], title: str = "Clinical Summary Dashboard") -> str:
    """
    Generate a self-contained, interactive HTML dashboard from parsed C-CDA JSON data.
    Designed for Canvas UI with Light/Dark mode, responsive grid, and high contrast.
    """
    meta = data.get("document_meta", {})
    patient = data.get("patient", {})
    summary = data.get("summary", {})
    sections = data.get("sections", {})
    
    patient_name = (patient.get("name") or {}).get("full_name", summary.get("patient_name", "Unknown Patient"))
    dob = patient.get("birth_time", summary.get("date_of_birth", "N/A"))
    gender = (patient.get("gender") or {}).get("display_name", summary.get("gender", "N/A"))
    doc_title = meta.get("title", "Clinical Document")
    doc_date = meta.get("effective_time", "N/A")
    
    json_payload = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    
    # Allergies
    allergies_list = sections.get("allergies", {}).get("entries", [])
    # Medications
    meds_list = sections.get("medications", {}).get("entries", [])
    # Problems
    problems_list = sections.get("problems", {}).get("entries", [])
    # Vitals
    vitals_panels = sections.get("vital_signs", {}).get("panels", [])
    vitals_flat = []
    for p in vitals_panels:
        for m in p.get("measurements", []):
            vitals_flat.append({
                "name": (m.get("vital_sign") or {}).get("display_name", "Measurement"),
                "value": (m.get("value") or {}).get("value", ""),
                "unit": (m.get("value") or {}).get("unit", ""),
                "interpretation": (m.get("interpretation") or {}).get("display_name", "Normal"),
                "date": p.get("date", "")
            })
    # Labs
    labs_list = sections.get("results", {}).get("results", [])
    # Immunizations
    imm_list = sections.get("immunizations", {}).get("entries", [])
    # Encounters
    enc_list = sections.get("encounters", {}).get("entries", [])
    # Procedures
    proc_list = sections.get("procedures", {}).get("entries", [])
    
    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{patient_name} - {doc_title}</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    body {{ font-family: var(--font-sans); }}
    pre, code {{ font-family: var(--font-mono); }}
    .code-block {{ background-color: #0f172a; color: #e2e8f0; }}
    .light .code-block {{ background-color: #f8fafc; color: #1e293b; border-color: #e2e8f0; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 transition-colors duration-200 antialiased min-h-screen p-4 sm:p-6">
  <div class="max-w-7xl mx-auto">
    
    <!-- Top Bar -->
    <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl mb-6">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-blue-500/20">
          🏥
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-xl font-extrabold text-white tracking-tight">{patient_name}</h1>
            <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">C-CDA Canvas</span>
          </div>
          <p class="text-xs text-slate-400 mt-0.5">
            DOB: <strong class="text-slate-200">{dob}</strong> • Gender: <strong class="text-slate-200">{gender}</strong> • Doc: <span class="text-slate-300">{doc_title}</span>
          </p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <button onclick="toggleTheme()" class="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:text-white hover:bg-slate-700 transition-all flex items-center space-x-1.5">
          <span id="themeText">☀️ Light Mode</span>
        </button>
        <button onclick="toggleRawJson()" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition-all shadow-md">
          {'{ }'} Raw JSON
        </button>
      </div>
    </header>

    <!-- Raw JSON Inspector Modal / Collapsible -->
    <div id="rawJsonSection" class="hidden mb-6 rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-bold text-slate-300 uppercase font-mono">Parsed Structured JSON Payload</span>
        <button onclick="copyRawJson()" class="text-xs text-blue-400 hover:underline">Copy JSON</button>
      </div>
      <pre class="p-4 rounded-xl code-block text-xs font-mono max-h-96 overflow-auto" id="jsonPayloadArea"><code>{json_payload}</code></pre>
    </div>

    <!-- Metric Counts Summary -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 mb-6">
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
        <div class="text-xs text-slate-400">Allergies</div>
        <div class="text-xl font-extrabold text-red-400">{len(allergies_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
        <div class="text-xs text-slate-400">Medications</div>
        <div class="text-xl font-extrabold text-emerald-400">{len(meds_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
        <div class="text-xs text-slate-400">Conditions</div>
        <div class="text-xl font-extrabold text-amber-400">{len(problems_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
        <div class="text-xs text-slate-400">Vital Signs</div>
        <div class="text-xl font-extrabold text-blue-400">{len(vitals_flat)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
        <div class="text-xs text-slate-400">Lab Results</div>
        <div class="text-xl font-extrabold text-purple-400">{len(labs_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
        <div class="text-xs text-slate-400">Immunizations</div>
        <div class="text-xl font-extrabold text-indigo-400">{len(imm_list)}</div>
      </div>
    </div>

    <!-- Two-Column Clinical Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Problems & Conditions Card -->
      <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <h3 class="text-sm font-bold text-white flex items-center space-x-2">
            <span>📋</span><span>Problems &amp; Conditions</span>
          </h3>
          <span class="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">{len(problems_list)} Active</span>
        </div>
        <div class="space-y-3">
          {"".join([f'''
          <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-100">{(p.get("problem") or {}).get("display_name", "Unknown Problem")}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">{p.get("status", "active")}</span>
            </div>
            <div class="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
              <span>SNOMED: <strong class="text-slate-300">{(p.get("problem") or {}).get("code", "N/A")}</strong></span>
              <span>Onset: <strong class="text-slate-300">{(p.get("effective_time") if isinstance(p.get("effective_time"), str) else (p.get("effective_time") or {}).get("low", "N/A"))}</strong></span>
            </div>
          </div>''' for p in problems_list]) if problems_list else '<div class="text-xs text-slate-500 py-4 text-center">No problems recorded</div>'}
        </div>
      </div>

      <!-- Medications Card -->
      <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <h3 class="text-sm font-bold text-white flex items-center space-x-2">
            <span>💊</span><span>Medications</span>
          </h3>
          <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">{len(meds_list)} Prescriptions</span>
        </div>
        <div class="space-y-3">
          {"".join([f'''
          <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-100">{(m.get("medication") or {}).get("display_name", "Unknown Medication")}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">{(m.get("dose") or {}).get("formatted", "")}</span>
            </div>
            <div class="mt-1 text-xs text-slate-400 flex flex-wrap gap-2">
              <span>Route: <strong class="text-slate-300">{(m.get("route") or {}).get("display_name", "Oral")}</strong></span>
              <span>Schedule: <strong class="text-slate-300">{(m.get("schedule") or {}).get("period", {}).get("human_readable", "Standard")}</strong></span>
              <span>RxNorm: <strong class="text-slate-300">{(m.get("medication") or {}).get("code", "N/A")}</strong></span>
            </div>
          </div>''' for m in meds_list]) if meds_list else '<div class="text-xs text-slate-500 py-4 text-center">No medications recorded</div>'}
        </div>
      </div>

      <!-- Allergies Card -->
      <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <h3 class="text-sm font-bold text-white flex items-center space-x-2">
            <span>🛡️</span><span>Allergies &amp; Intolerances</span>
          </h3>
          <span class="text-xs px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30">{len(allergies_list)} Alerts</span>
        </div>
        <div class="space-y-3">
          {"".join([f'''
          <div class="p-3 rounded-xl bg-red-950/20 border border-red-800/40">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-red-200">{(a.get("substance") or {}).get("display_name", "Substance")}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-semibold">{a.get("status", "active")}</span>
            </div>
            <div class="mt-1 text-xs text-slate-300">
              Reactions: {", ".join([((rx.get("reaction") or {}).get("display_name", "") + " (" + (rx.get("severity") or {}).get("display_name", "") + ")") for rx in a.get("reactions", [])])}
            </div>
          </div>''' for a in allergies_list]) if allergies_list else '<div class="text-xs text-slate-500 py-4 text-center">No allergies recorded</div>'}
        </div>
      </div>

      <!-- Vital Signs & Diagnostic Results -->
      <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <h3 class="text-sm font-bold text-white flex items-center space-x-2">
            <span>🧪</span><span>Vitals &amp; Diagnostic Labs</span>
          </h3>
          <span class="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30">{len(vitals_flat) + len(labs_list)} Results</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          {"".join([f'''
          <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
            <div class="text-xs text-slate-400 truncate">{v.get("name")}</div>
            <div class="text-base font-bold text-white mt-0.5">{v.get("value")} <span class="text-xs text-slate-400 font-normal">{v.get("unit")}</span></div>
            <div class="text-[10px] text-emerald-400 mt-0.5">{v.get("interpretation")}</div>
          </div>''' for v in vitals_flat[:4]])}
          {"".join([f'''
          <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
            <div class="text-xs text-slate-400 truncate">{(l.get("test") or {}).get("display_name", "Lab Test")}</div>
            <div class="text-base font-bold text-blue-400 mt-0.5">{(l.get("value") or {}).get("value")} <span class="text-xs text-slate-400 font-normal">{(l.get("value") or {}).get("unit")}</span></div>
            <div class="text-[10px] text-amber-400 mt-0.5">{(l.get("interpretation") or {}).get("display_name", "Normal")}</div>
          </div>''' for l in labs_list[:4]])}
        </div>
      </div>

    </div>

    <!-- Footer -->
    <footer class="mt-8 text-center text-xs text-slate-500 py-4 border-t border-slate-800">
      Antigravity / Gemini Enterprise App C-CDA Canvas Visualizer • {doc_title} • Generated: {doc_date}
    </footer>

  </div>

  <script>
    let isDark = true;
    function toggleTheme() {{
      const html = document.documentElement;
      isDark = !isDark;
      if (isDark) {{
        html.classList.remove("light");
        html.classList.add("dark");
        document.body.className = "bg-slate-950 text-slate-100 transition-colors duration-200 antialiased min-h-screen p-4 sm:p-6";
        document.getElementById("themeText").textContent = "☀️ Light Mode";
      }} else {{
        html.classList.remove("dark");
        html.classList.add("light");
        document.body.className = "bg-slate-50 text-slate-900 transition-colors duration-200 antialiased min-h-screen p-4 sm:p-6";
        document.getElementById("themeText").textContent = "🌙 Dark Mode";
      }}
    }}

    function toggleRawJson() {{
      const sec = document.getElementById("rawJsonSection");
      sec.classList.toggle("hidden");
    }}

    function copyRawJson() {{
      const text = document.getElementById("jsonPayloadArea").textContent;
      navigator.clipboard.writeText(text).then(() => alert("JSON copied to clipboard!"));
    }}
  </script>
</body>
</html>
"""
    return html
