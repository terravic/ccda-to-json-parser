"""
HTML Visualizer Generator for Parsed C-CDA JSON Documents.
Renders an executive interactive patient dashboard for web browser viewing
with dual Input XML Document and Output JSON viewers.
"""

import html
import json
import os
from typing import Any, Dict, List, Optional


def generate_patient_dashboard_html(
    data: Dict[str, Any],
    title: str = "Clinical Summary Dashboard",
    raw_input: Optional[str] = None,
    input_filename: Optional[str] = None,
) -> str:
    """
    Generate a self-contained, interactive HTML dashboard from parsed C-CDA JSON data
    and original input XML file (C-CDA XML).
    Designed with Light/Dark mode, responsive grid, high contrast,
    and side-by-side or tabbed inspection of both input XML and output JSON files.
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
    doc_id = (meta.get("document_id") or {}).get("extension", "N/A")

    # If raw input is not provided, try to find a sample or generate representative XML
    if not raw_input:
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "samples",
            "sample_1_continuity_of_care_document.xml",
        )
        if os.path.exists(sample_path):
            try:
                with open(sample_path, "r", encoding="utf-8", errors="replace") as f:
                    raw_input = f.read()
                input_filename = input_filename or "sample_1_continuity_of_care_document.xml"
            except Exception:
                raw_input = "<!-- Source C-CDA XML content not directly provided during generation. -->"
        else:
            raw_input = "<!-- Source C-CDA XML content not directly provided during generation. -->"

    if not input_filename:
        input_filename = "clinical_document.xml"

    json_payload = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    escaped_raw_input = html.escape(raw_input)
    escaped_json_payload = html.escape(json_payload)

    # Allergies
    allergies_list = sections.get("allergies", {}).get("entries", [])
    # Medications
    meds_list = sections.get("medications", {}).get("entries", [])
    # Problems
    problems_list = sections.get("problems", {}).get("entries", [])
    # Vitals
    vitals_panels = sections.get("vital_signs", {}).get("panels", [])
    vitals_flat: List[Dict[str, Any]] = []
    for p in vitals_panels:
        for m in p.get("measurements", []):
            vitals_flat.append({
                "name": (m.get("vital_sign") or {}).get("display_name", "Measurement"),
                "value": (m.get("value") or {}).get("value", ""),
                "unit": (m.get("value") or {}).get("unit", ""),
                "interpretation": (m.get("interpretation") or {}).get("display_name", "Normal"),
                "date": p.get("date", ""),
            })
    # Labs
    labs_list = sections.get("results", {}).get("results", [])
    # Immunizations
    imm_list = sections.get("immunizations", {}).get("entries", [])
    # Encounters
    enc_list = sections.get("encounters", {}).get("entries", [])
    # Procedures
    proc_list = sections.get("procedures", {}).get("entries", [])
    # Social History
    social_entries = sections.get("social_history", {}).get("entries", [])

    # Calculate statistics
    xml_lines_count = len(raw_input.splitlines()) if raw_input else 0
    xml_size_kb = round(len(raw_input.encode("utf-8")) / 1024, 1) if raw_input else 0
    json_lines_count = len(json_payload.splitlines())
    json_size_kb = round(len(json_payload.encode("utf-8")) / 1024, 1)

    # Safe serialized data for JS variables
    js_raw_input = json.dumps(raw_input)
    js_json_payload = json.dumps(json_payload)
    js_input_filename = json.dumps(input_filename)

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(patient_name)} - {html.escape(doc_title)} | C-CDA Visualizer</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {{
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    body {{ font-family: var(--font-sans); }}
    pre, code {{ font-family: var(--font-mono); }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.05); }}
    .dark ::-webkit-scrollbar-track {{ background: rgba(255, 255, 255, 0.05); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(150, 150, 150, 0.3); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(150, 150, 150, 0.5); }}
    .code-block {{ background-color: #0f172a; color: #e2e8f0; }}
    .light .code-block {{ background-color: #f8fafc; color: #1e293b; border-color: #e2e8f0; }}
    .tab-btn-active {{
      border-bottom: 2px solid #3b82f6;
      color: #3b82f6 !important;
      font-weight: 700;
      background-color: rgba(59, 130, 246, 0.1) !important;
    }}
    .search-match {{
      background-color: #f59e0b;
      color: #000;
      border-radius: 2px;
      padding: 0 2px;
    }}
    .xml-syntax-tag {{ color: #60a5fa; font-weight: 600; }}
    .xml-syntax-attr {{ color: #93c5fd; }}
    .xml-syntax-val {{ color: #34d399; }}
    .xml-syntax-comm {{ color: #64748b; font-style: italic; }}
    .light .xml-syntax-tag {{ color: #1d4ed8; font-weight: 600; }}
    .light .xml-syntax-attr {{ color: #0284c7; }}
    .light .xml-syntax-val {{ color: #059669; }}
    .light .xml-syntax-comm {{ color: #94a3b8; font-style: italic; }}
    .drag-over-active {{
      border-color: #3b82f6 !important;
      background-color: rgba(59, 130, 246, 0.08) !important;
      transform: scale(1.005);
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 transition-colors duration-200 antialiased min-h-screen p-4 sm:p-6">
  <div class="max-w-7xl mx-auto">
    
    <!-- Top Executive Header Bar -->
    <header class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl mb-6">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-blue-500/20">
          🏥
        </div>
        <div>
          <div class="flex items-center space-x-2 flex-wrap">
            <h1 class="text-xl font-extrabold text-white tracking-tight">{html.escape(patient_name)}</h1>
            <span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">C-CDA Viewer</span>
            <span class="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-800 text-slate-400 border border-slate-700">ID: {html.escape(str(doc_id))}</span>
          </div>
          <p class="text-xs text-slate-400 mt-1 flex flex-wrap items-center gap-2">
            <span>DOB: <strong class="text-slate-200">{html.escape(str(dob))}</strong></span>
            <span>•</span>
            <span>Gender: <strong class="text-slate-200">{html.escape(str(gender))}</strong></span>
            <span>•</span>
            <span>Doc: <span class="text-slate-300 font-medium">{html.escape(str(doc_title))}</span></span>
            <span>•</span>
            <span>Date: <span class="text-slate-300">{html.escape(str(doc_date))}</span></span>
          </p>
        </div>
      </div>

      <!-- Action Buttons: Input XML File, Output JSON, Split View, Theme Toggle -->
      <div class="flex items-center flex-wrap gap-2">
        <button 
          onclick="openInspectorTab('input')" 
          class="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs font-semibold text-slate-200 hover:text-white transition-all flex items-center space-x-1.5 shadow-sm"
          title="Inspect the source C-CDA XML input file"
        >
          <span>📄</span>
          <span>Input XML File</span>
          <span class="px-1.5 py-0.2 text-[10px] rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">{xml_size_kb} KB</span>
        </button>

        <button 
          onclick="openInspectorTab('json')" 
          class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition-all shadow-md flex items-center space-x-1.5"
          title="Inspect the structured Output JSON payload"
        >
          <span>{'{ }'}</span>
          <span>Output JSON</span>
          <span class="px-1.5 py-0.2 text-[10px] rounded bg-white/20 text-white font-mono">{json_size_kb} KB</span>
        </button>

        <button 
          onclick="openInspectorTab('split')" 
          class="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-all shadow-md flex items-center space-x-1.5"
          title="Compare Input XML and Output JSON side-by-side"
        >
          <span>↔️</span>
          <span>Side-by-Side (XML vs JSON)</span>
        </button>

        <button 
          onclick="openInspectorTab('table')" 
          class="px-3 py-1.5 rounded-lg bg-emerald-600/90 hover:bg-emerald-500 text-xs font-semibold text-white transition-all shadow-md flex items-center space-x-1.5"
          title="View clinical structured tables"
        >
          <span>📊</span>
          <span>Clinical Tables</span>
        </button>

        <!-- Hidden File Input & Upload Trigger -->
        <input type="file" id="fileUploadInput" class="hidden" accept=".xml,.ccda,.cda,.json" onchange="handleFileSelected(event)">
        <button 
          onclick="document.getElementById('fileUploadInput').click()" 
          class="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs text-slate-300 hover:text-white transition-all flex items-center space-x-1"
          title="Upload or inspect any local C-CDA XML file"
        >
          <span>📁</span>
          <span>Load XML</span>
        </button>

        <!-- Theme Toggle -->
        <button 
          onclick="toggleTheme()" 
          class="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:text-white hover:bg-slate-700 transition-all flex items-center space-x-1.5"
          title="Toggle Light / Dark Mode"
        >
          <span id="themeText">☀️ Light Mode</span>
        </button>
      </div>
    </header>

    <!-- Interactive Data Inspector Container (Collapsible Modal / Panel) -->
    <div id="dataInspectorPanel" class="hidden mb-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl overflow-hidden transition-all duration-300">
      
      <!-- Panel Header & Navigation Tabs -->
      <div class="px-5 py-3.5 bg-slate-800/80 border-b border-slate-700 flex flex-col md:flex-row md:items-center justify-between gap-3">
        
        <!-- Left: Tab Selectors -->
        <div class="flex items-center space-x-2 overflow-x-auto pb-1 md:pb-0 scrollbar-thin">
          <button 
            id="tabBtnInput" 
            onclick="switchInspectorTab('input')" 
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700/60 transition-all flex items-center space-x-2"
          >
            <span>📄</span>
            <span>Input XML File</span>
            <span id="inputBadge" class="px-1.5 py-0.5 text-[10px] rounded bg-slate-700 text-slate-300 font-mono">{xml_lines_count} lines</span>
          </button>

          <button 
            id="tabBtnJson" 
            onclick="switchInspectorTab('json')" 
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700/60 transition-all flex items-center space-x-2"
          >
            <span>{'{ }'}</span>
            <span>Output JSON</span>
            <span id="jsonBadge" class="px-1.5 py-0.5 text-[10px] rounded bg-slate-700 text-slate-300 font-mono">{json_lines_count} lines</span>
          </button>

          <button 
            id="tabBtnSplit" 
            onclick="switchInspectorTab('split')" 
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700/60 transition-all flex items-center space-x-2"
          >
            <span>↔️</span>
            <span>Side-by-Side (XML vs JSON)</span>
          </button>

          <button 
            id="tabBtnTable" 
            onclick="switchInspectorTab('table')" 
            class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-700/60 transition-all flex items-center space-x-2"
          >
            <span>📊</span>
            <span>Clinical Tables</span>
          </button>
        </div>

        <!-- Right: Actions (Search, Copy, Download, Close) -->
        <div class="flex items-center space-x-2.5">
          <!-- Real-time code search -->
          <div class="relative">
            <input 
              type="text" 
              id="inspectorSearchInput" 
              placeholder="Search in viewer..." 
              class="w-40 sm:w-56 px-2.5 py-1 pl-7 pr-24 text-xs rounded-lg bg-slate-950/70 border border-slate-700 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
              oninput="handleSearchContent(this.value)"
              onkeydown="handleSearchKeydown(event)"
            />
            <span class="absolute left-2 top-1.5 text-slate-400 text-xs">🔍</span>
            <span id="searchMatchCount" class="hidden absolute right-2 top-1.5 text-[10px] text-amber-400 font-mono font-semibold">0 hits</span>
          </div>

          <button 
            onclick="copyActiveContent()" 
            class="px-2.5 py-1 rounded-lg bg-slate-700/70 hover:bg-slate-600 text-xs text-slate-200 hover:text-white transition-all flex items-center space-x-1"
            title="Copy active view content to clipboard"
          >
            <span id="copyBtnIcon">📋</span>
            <span id="copyBtnText">Copy</span>
          </button>

          <button 
            onclick="downloadActiveContent()" 
            class="px-2.5 py-1 rounded-lg bg-slate-700/70 hover:bg-slate-600 text-xs text-slate-200 hover:text-white transition-all flex items-center space-x-1"
            title="Download active file"
          >
            <span>⬇️</span>
            <span>Download</span>
          </button>

          <button 
            onclick="toggleInspectorPanel()" 
            class="px-2.5 py-1 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-xs text-red-300 hover:text-red-100 transition-all font-bold"
            title="Close inspector panel"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- Drag & Drop Zone Bar -->
      <div 
        id="dropZoneBanner" 
        class="px-5 py-2 bg-blue-950/30 border-b border-blue-900/30 flex items-center justify-between text-xs text-blue-300 transition-all"
        ondragover="handleDragOver(event)"
        ondragleave="handleDragLeave(event)"
        ondrop="handleFileDrop(event)"
      >
        <div class="flex items-center space-x-2 truncate">
          <span>📁</span>
          <span>Loaded Source: <strong id="activeFileName" class="text-white font-mono">{html.escape(input_filename)}</strong></span>
          <span class="text-slate-400 font-normal">| Drag &amp; drop any C-CDA XML (.xml, .ccda, .cda) file directly into this dashboard</span>
        </div>
        <button onclick="document.getElementById('fileUploadInput').click()" class="text-blue-400 hover:underline text-[11px] whitespace-nowrap">
          Choose XML file...
        </button>
      </div>

      <!-- Search Notification Banner -->
      <div id="searchNotificationArea" class="hidden px-4 pt-3"></div>

      <!-- Tab View 1: Input XML File -->
      <div id="viewContainerInput" class="p-4">
        <div class="flex items-center justify-between mb-2 text-xs text-slate-400 px-1">
          <span>Source Input Document (HL7 C-CDA R2.1 XML)</span>
          <span class="font-mono text-[11px]">Format: HL7 C-CDA XML</span>
        </div>
        <pre class="p-4 rounded-xl code-block text-xs font-mono max-h-[500px] overflow-auto leading-relaxed" id="xmlPayloadArea"><code>{escaped_raw_input}</code></pre>
      </div>

      <!-- Tab View 2: Output JSON -->
      <div id="viewContainerJson" class="hidden p-4">
        <div class="flex items-center justify-between mb-2 text-xs text-slate-400 px-1">
          <span>Target Parsed Structured JSON Payload</span>
          <span class="font-mono text-[11px]">Format: JSON Schema Compliant</span>
        </div>
        <pre class="p-4 rounded-xl code-block text-xs font-mono max-h-[500px] overflow-auto leading-relaxed" id="jsonPayloadArea"><code>{escaped_json_payload}</code></pre>
      </div>

      <!-- Tab View 3: Side-by-Side Comparison -->
      <div id="viewContainerSplit" class="hidden p-4">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <!-- Left: Input XML File -->
          <div class="flex flex-col rounded-xl border border-slate-800 bg-slate-950/60 overflow-hidden">
            <div class="px-3 py-2 bg-slate-800/60 border-b border-slate-700 text-xs font-semibold text-blue-400 flex items-center justify-between">
              <span>📄 Input XML: {html.escape(input_filename)}</span>
              <button onclick="copySnippetText('xmlPayloadArea')" class="text-slate-400 hover:text-white text-[11px]">Copy XML</button>
            </div>
            <pre class="p-3 text-xs font-mono max-h-[460px] overflow-auto leading-relaxed text-slate-200 code-block" id="splitXmlArea"><code>{escaped_raw_input}</code></pre>
          </div>

          <!-- Right: Output JSON -->
          <div class="flex flex-col rounded-xl border border-slate-800 bg-slate-950/60 overflow-hidden">
            <div class="px-3 py-2 bg-slate-800/60 border-b border-slate-700 text-xs font-semibold text-emerald-400 flex items-center justify-between">
              <span>{'{ }'} Output JSON: structured_output.json</span>
              <button onclick="copySnippetText('jsonPayloadArea')" class="text-slate-400 hover:text-white text-[11px]">Copy JSON</button>
            </div>
            <pre class="p-3 text-xs font-mono max-h-[460px] overflow-auto leading-relaxed text-slate-200 code-block" id="splitJsonArea"><code>{escaped_json_payload}</code></pre>
          </div>
        </div>
      </div>

      <!-- Tab View 4: Clinical Tables View -->
      <div id="viewContainerTable" class="hidden p-4">
        <div class="flex items-center justify-between mb-3 text-xs text-slate-400">
          <div class="flex items-center space-x-2">
            <span>Clinical Domain Tables</span>
            <select id="tableSectionSelector" onchange="renderClinicalTable(this.value)" class="px-2 py-1 text-xs rounded bg-slate-800 border border-slate-700 text-slate-200">
              <option value="medications">Medications Table ({len(meds_list)} items)</option>
              <option value="allergies">Allergies Table ({len(allergies_list)} items)</option>
              <option value="problems">Problems &amp; Conditions Table ({len(problems_list)} items)</option>
              <option value="vitals">Vital Signs Table ({len(vitals_flat)} items)</option>
              <option value="labs">Diagnostic Results Table ({len(labs_list)} items)</option>
              <option value="immunizations">Immunizations Table ({len(imm_list)} items)</option>
              <option value="encounters">Encounters Table ({len(enc_list)} items)</option>
            </select>
          </div>
          <span class="text-slate-400 text-[11px]">Structured Clinical Table Representation</span>
        </div>
        
        <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/70 p-3 max-h-[480px]">
          <div id="clinicalTableContainer">
            <!-- Rendered by JS -->
          </div>
        </div>
      </div>

    </div>


    <!-- Metric Counts Summary Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 mb-6">
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center shadow-md hover:border-slate-700 transition-all cursor-pointer" onclick="openInspectorTab('table'); document.getElementById('tableSectionSelector').value='allergies'; renderClinicalTable('allergies');">
        <div class="text-xs text-slate-400">Allergies</div>
        <div class="text-xl font-extrabold text-red-400">{len(allergies_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center shadow-md hover:border-slate-700 transition-all cursor-pointer" onclick="openInspectorTab('table'); document.getElementById('tableSectionSelector').value='medications'; renderClinicalTable('medications');">
        <div class="text-xs text-slate-400">Medications</div>
        <div class="text-xl font-extrabold text-emerald-400">{len(meds_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center shadow-md hover:border-slate-700 transition-all cursor-pointer" onclick="openInspectorTab('table'); document.getElementById('tableSectionSelector').value='problems'; renderClinicalTable('problems');">
        <div class="text-xs text-slate-400">Conditions</div>
        <div class="text-xl font-extrabold text-amber-400">{len(problems_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center shadow-md hover:border-slate-700 transition-all cursor-pointer" onclick="openInspectorTab('table'); document.getElementById('tableSectionSelector').value='vitals'; renderClinicalTable('vitals');">
        <div class="text-xs text-slate-400">Vital Signs</div>
        <div class="text-xl font-extrabold text-blue-400">{len(vitals_flat)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center shadow-md hover:border-slate-700 transition-all cursor-pointer" onclick="openInspectorTab('table'); document.getElementById('tableSectionSelector').value='labs'; renderClinicalTable('labs');">
        <div class="text-xs text-slate-400">Lab Results</div>
        <div class="text-xl font-extrabold text-purple-400">{len(labs_list)}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center shadow-md hover:border-slate-700 transition-all cursor-pointer" onclick="openInspectorTab('table'); document.getElementById('tableSectionSelector').value='immunizations'; renderClinicalTable('immunizations');">
        <div class="text-xs text-slate-400">Immunizations</div>
        <div class="text-xl font-extrabold text-indigo-400">{len(imm_list)}</div>
      </div>
    </div>

    <!-- Main Two-Column Clinical Grid -->
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
              <span class="text-sm font-semibold text-slate-100">{html.escape(str((p.get("problem") or {}).get("display_name", "Unknown Problem")))}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">{html.escape(str(p.get("status", "active")))}</span>
            </div>
            <div class="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
              <span>SNOMED: <strong class="text-slate-300">{html.escape(str((p.get("problem") or {}).get("code", "N/A")))}</strong></span>
              <span>Onset: <strong class="text-slate-300">{html.escape(str(p.get("effective_time") if isinstance(p.get("effective_time"), str) else (p.get("effective_time") or {}).get("low", "N/A")))}</strong></span>
            </div>
          </div>''' for p in problems_list]) if problems_list else '<div class="text-xs text-slate-500 py-4 text-center">No problems recorded</div>'}
        </div>
      </div>

      <!-- Medications Card -->
      <div class="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
        <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <h3 class="text-sm font-bold text-white flex items-center space-x-2">
            <span>💊</span><span>Medications &amp; Prescriptions</span>
          </h3>
          <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">{len(meds_list)} Prescriptions</span>
        </div>
        <div class="space-y-3">
          {"".join([f'''
          <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-100">{html.escape(str((m.get("medication") or {}).get("display_name", "Unknown Medication")))}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">{html.escape(str((m.get("dose") or {}).get("formatted", "")))}</span>
            </div>
            <div class="mt-1 text-xs text-slate-400 flex flex-wrap gap-2">
              <span>Route: <strong class="text-slate-300">{html.escape(str((m.get("route") or {}).get("display_name", "Oral")))}</strong></span>
              <span>Schedule: <strong class="text-slate-300">{html.escape(str((m.get("schedule") or {}).get("period", {}).get("human_readable", "Standard")))}</strong></span>
              <span>RxNorm: <strong class="text-slate-300">{html.escape(str((m.get("medication") or {}).get("code", "N/A")))}</strong></span>
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
              <span class="text-sm font-semibold text-red-200">{html.escape(str((a.get("substance") or {}).get("display_name", "Substance")))}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-300 font-semibold">{html.escape(str(a.get("status", "active")))}</span>
            </div>
            <div class="mt-1 text-xs text-slate-300">
              Reactions: {html.escape(", ".join([((rx.get("reaction") or {}).get("display_name", "") + " (" + (rx.get("severity") or {}).get("display_name", "") + ")") for rx in a.get("reactions", [])]))}
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
            <div class="text-xs text-slate-400 truncate">{html.escape(str(v.get("name")))}</div>
            <div class="text-base font-bold text-white mt-0.5">{html.escape(str(v.get("value")))} <span class="text-xs text-slate-400 font-normal">{html.escape(str(v.get("unit")))}</span></div>
            <div class="text-[10px] text-emerald-400 mt-0.5">{html.escape(str(v.get("interpretation")))}</div>
          </div>''' for v in vitals_flat[:4]])}
          {"".join([f'''
          <div class="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
            <div class="text-xs text-slate-400 truncate">{html.escape(str((l.get("test") or {}).get("display_name", "Lab Test")))}</div>
            <div class="text-base font-bold text-blue-400 mt-0.5">{html.escape(str((l.get("value") or {}).get("value")))} <span class="text-xs text-slate-400 font-normal">{html.escape(str((l.get("value") or {}).get("unit")))}</span></div>
            <div class="text-[10px] text-amber-400 mt-0.5">{html.escape(str((l.get("interpretation") or {}).get("display_name", "Normal")))}</div>
          </div>''' for l in labs_list[:4]])}
        </div>
      </div>

    </div>

    <!-- Demographics & Document Details Card -->
    <div class="mt-6 p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg">
      <h3 class="text-sm font-bold text-white mb-3 border-b border-slate-800 pb-2 flex items-center space-x-2">
        <span>👤</span><span>Patient Demographics &amp; Document Details</span>
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
        <div>
          <span class="text-slate-500 block">Addresses:</span>
          <span class="text-slate-200">{html.escape(str(", ".join([a.get("formatted", "") for a in patient.get("addresses", []) if a.get("formatted")]) or "N/A"))}</span>
        </div>
        <div>
          <span class="text-slate-500 block">Phone / Telecom:</span>
          <span class="text-slate-200">{html.escape(str(", ".join([t.get("value", "") for t in patient.get("telecoms", []) if t.get("value")]) or "N/A"))}</span>
        </div>
        <div>
          <span class="text-slate-500 block">Custodian / Facility:</span>
          <span class="text-slate-200">{html.escape(str((meta.get("custodian") or {}).get("name", "N/A")))}</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="mt-8 text-center text-xs text-slate-500 py-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-2">
      <div>
        HL7 C-CDA to JSON Interactive Dashboard • {html.escape(str(doc_title))} • Generated: {html.escape(str(doc_date))}
      </div>
      <div class="flex items-center space-x-3 text-slate-400">
        <button onclick="openInspectorTab('input')" class="hover:text-blue-400 transition-colors">View Input XML</button>
        <span>•</span>
        <button onclick="openInspectorTab('json')" class="hover:text-emerald-400 transition-colors">View Output JSON</button>
        <span>•</span>
        <button onclick="openInspectorTab('table')" class="hover:text-amber-400 transition-colors">Clinical Tables</button>
      </div>
    </footer>

  </div>

  <!-- Client-side Interactive Logic -->
  <script>
    // State variables
    let isDark = true;
    let currentTab = 'input';
    let rawInputContent = {js_raw_input};
    let jsonOutputContent = {js_json_payload};
    let currentFileName = {js_input_filename};
    const structuredData = {json_payload};

    // Initialize clinical tables on load
    document.addEventListener('DOMContentLoaded', () => {{
      renderClinicalTable('medications');
    }});

    // Light / Dark Theme toggle
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

    // Toggle Inspector Panel open / closed
    function toggleInspectorPanel() {{
      const panel = document.getElementById("dataInspectorPanel");
      panel.classList.toggle("hidden");
    }}

    // Open Inspector and focus specific tab
    function openInspectorTab(tab) {{
      const panel = document.getElementById("dataInspectorPanel");
      panel.classList.remove("hidden");
      switchInspectorTab(tab);
      // Smooth scroll to inspector
      panel.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    // Switch between Inspector Tabs: 'input', 'json', 'split', 'table'
    function switchInspectorTab(tab) {{
      currentTab = tab;
      
      // Hide all view containers
      document.getElementById("viewContainerInput").classList.add("hidden");
      document.getElementById("viewContainerJson").classList.add("hidden");
      document.getElementById("viewContainerSplit").classList.add("hidden");
      document.getElementById("viewContainerTable").classList.add("hidden");

      // Reset tab button states
      const tabBtns = ['tabBtnInput', 'tabBtnJson', 'tabBtnSplit', 'tabBtnTable'];
      tabBtns.forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{
          el.classList.remove("tab-btn-active", "bg-blue-600/20", "text-blue-400", "border-b-2", "border-blue-500");
          el.classList.add("text-slate-300");
        }}
      }});

      // Show selected container and highlight active button
      if (tab === 'input') {{
        document.getElementById("viewContainerInput").classList.remove("hidden");
        document.getElementById("tabBtnInput").classList.add("tab-btn-active", "bg-blue-600/20", "text-blue-400", "border-b-2", "border-blue-500");
      }} else if (tab === 'json') {{
        document.getElementById("viewContainerJson").classList.remove("hidden");
        document.getElementById("tabBtnJson").classList.add("tab-btn-active", "bg-blue-600/20", "text-blue-400", "border-b-2", "border-blue-500");
      }} else if (tab === 'split') {{
        document.getElementById("viewContainerSplit").classList.remove("hidden");
        document.getElementById("tabBtnSplit").classList.add("tab-btn-active", "bg-blue-600/20", "text-blue-400", "border-b-2", "border-blue-500");
      }} else if (tab === 'table') {{
        document.getElementById("viewContainerTable").classList.remove("hidden");
        document.getElementById("tabBtnTable").classList.add("tab-btn-active", "bg-blue-600/20", "text-blue-400", "border-b-2", "border-blue-500");
      }}

      // Clear search
      const searchInput = document.getElementById("inspectorSearchInput");
      if (searchInput && searchInput.value) {{
        handleSearchContent(searchInput.value);
      }}
    }}

    // Copy active tab content to clipboard
    function copyActiveContent() {{
      let textToCopy = "";
      if (currentTab === 'input') {{
        textToCopy = rawInputContent;
      }} else if (currentTab === 'json') {{
        textToCopy = jsonOutputContent;
      }} else if (currentTab === 'split') {{
        textToCopy = "// === SOURCE INPUT FILE (" + currentFileName + ") ===\\n" + rawInputContent + "\\n\\n// === PARSED JSON OUTPUT ===\\n" + jsonOutputContent;
      }} else if (currentTab === 'table') {{
        const tableContainer = document.getElementById("clinicalTableContainer");
        textToCopy = tableContainer.innerText || "";
      }}

      navigator.clipboard.writeText(textToCopy).then(() => {{
        const btnText = document.getElementById("copyBtnText");
        const btnIcon = document.getElementById("copyBtnIcon");
        btnText.textContent = "Copied!";
        btnIcon.textContent = "✓";
        setTimeout(() => {{
          btnText.textContent = "Copy";
          btnIcon.textContent = "📋";
        }}, 2000);
      }});
    }}

    // Copy specific element text
    function copySnippetText(elementId) {{
      const text = document.getElementById(elementId).textContent;
      navigator.clipboard.writeText(text).then(() => {{
        alert("Content copied to clipboard!");
      }});
    }}

    // Download active file
    function downloadActiveContent() {{
      let content = "";
      let filename = "export.txt";
      let mimeType = "text/plain";

      if (currentTab === 'input') {{
        content = rawInputContent;
        filename = currentFileName || "input_clinical_document.xml";
        mimeType = filename.endsWith(".json") ? "application/json" : "application/xml";
      }} else if (currentTab === 'json') {{
        content = jsonOutputContent;
        filename = (currentFileName.replace(/\\.[^/.]+$/, "") || "clinical_document") + "_parsed.json";
        mimeType = "application/json";
      }} else if (currentTab === 'split') {{
        content = "// === SOURCE INPUT XML ===\\n" + rawInputContent + "\\n\\n// === PARSED JSON ===\\n" + jsonOutputContent;
        filename = "ccda_input_and_output.txt";
      }} else if (currentTab === 'table') {{
        content = document.getElementById("clinicalTableContainer").innerText || "";
        filename = "clinical_table_export.txt";
      }}

      const blob = new Blob([content], {{ type: mimeType }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }}

    // Real-time search inside code views
    function handleSearchContent(query) {{
      const matchBadge = document.getElementById("searchMatchCount");
      const notifArea = document.getElementById("searchNotificationArea");
      
      if (!query || query.trim() === "") {{
        matchBadge.classList.add("hidden");
        if (notifArea) notifArea.classList.add("hidden");
        // Reset contents
        document.getElementById("xmlPayloadArea").innerHTML = "<code>" + escapeHtml(rawInputContent) + "</code>";
        document.getElementById("jsonPayloadArea").innerHTML = "<code>" + escapeHtml(jsonOutputContent) + "</code>";
        document.getElementById("splitXmlArea").innerHTML = "<code>" + escapeHtml(rawInputContent) + "</code>";
        document.getElementById("splitJsonArea").innerHTML = "<code>" + escapeHtml(jsonOutputContent) + "</code>";
        return;
      }}

      const cleanQuery = query.trim();
      const escapedQuery = escapeHtml(cleanQuery);
      const regex = new RegExp("(" + escapeRegExp(escapedQuery) + ")", "gi");

      let totalHits = 0;
      if (currentTab === 'json') {{
        const matches = escapeHtml(jsonOutputContent).match(regex);
        if (matches) totalHits = matches.length;
      }} else if (currentTab === 'input') {{
        const matches = escapeHtml(rawInputContent).match(regex);
        if (matches) totalHits = matches.length;
      }} else if (currentTab === 'split') {{
        const matchesXml = escapeHtml(rawInputContent).match(regex);
        const matchesJson = escapeHtml(jsonOutputContent).match(regex);
        totalHits = (matchesXml ? matchesXml.length : 0) + (matchesJson ? matchesJson.length : 0);
      }} else if (currentTab === 'table') {{
        const matchesJson = escapeHtml(jsonOutputContent).match(regex);
        if (matchesJson) totalHits = matchesJson.length;
      }}

      matchBadge.classList.remove("hidden");

      if (totalHits > 0) {{
        matchBadge.className = "absolute right-2 top-1.5 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold";
        matchBadge.textContent = totalHits + " match" + (totalHits === 1 ? "" : "es");
        if (notifArea) notifArea.classList.add("hidden");

        // Highlight in active element
        if (currentTab === 'input') {{
          document.getElementById("xmlPayloadArea").innerHTML = "<code>" + highlightText(rawInputContent, regex) + "</code>";
        }} else if (currentTab === 'json') {{
          document.getElementById("jsonPayloadArea").innerHTML = "<code>" + highlightText(jsonOutputContent, regex) + "</code>";
        }} else if (currentTab === 'split') {{
          document.getElementById("splitXmlArea").innerHTML = "<code>" + highlightText(rawInputContent, regex) + "</code>";
          document.getElementById("splitJsonArea").innerHTML = "<code>" + highlightText(jsonOutputContent, regex) + "</code>";
        }}

        // Auto-scroll to first match
        setTimeout(() => {{
          const firstMark = document.querySelector("#dataInspectorPanel mark.search-match");
          if (firstMark) {{
            firstMark.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
          }}
        }}, 50);

      }} else {{
        matchBadge.className = "absolute right-2 top-1.5 text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30 font-semibold";
        matchBadge.textContent = "0 matches (Not found)";

        if (notifArea) {{
          const docType = currentTab === 'json' ? 'JSON output' : currentTab === 'input' ? 'XML document' : 'active file';
          notifArea.innerHTML = `
            <div class="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-center justify-between">
              <span><strong>Not Found:</strong> The search query "<strong>${{escapeHtml(cleanQuery)}}</strong>" was not found in the processed ${{docType}}.</span>
              <button onclick="document.getElementById('inspectorSearchInput').value=''; handleSearchContent('');" class="px-2 py-0.5 rounded bg-rose-900/60 hover:bg-rose-800 text-rose-200 text-[11px] font-medium">Clear</button>
            </div>
          `;
          notifArea.classList.remove("hidden");
        }}
      }}
    }}

    function handleSearchKeydown(event) {{
      if (event.key === "Enter") {{
        event.preventDefault();
        const activeContainer = currentTab === 'input' ? document.getElementById("xmlPayloadArea") :
                                currentTab === 'json' ? document.getElementById("jsonPayloadArea") :
                                currentTab === 'split' ? document.getElementById("viewContainerSplit") :
                                document.getElementById("clinicalTableContainer");
        const firstMatch = activeContainer ? activeContainer.querySelector(".search-match") : document.querySelector(".search-match");
        if (firstMatch) {{
          firstMatch.scrollIntoView({{ behavior: "smooth", block: "center" }});
        }}
      }}
    }}

    function highlightText(text, regex) {{
      const escaped = escapeHtml(text);
      return escaped.replace(regex, '<mark class="search-match bg-amber-400 text-slate-950 font-bold px-0.5 rounded">$1</mark>');
    }}

    function escapeHtml(str) {{
      if (!str) return "";
      return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }}

    function escapeRegExp(str) {{
      return str.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    }}

    // Render clinical tables dynamically
    function renderClinicalTable(sectionKey) {{
      const container = document.getElementById("clinicalTableContainer");
      const sec = structuredData.sections || {{}};

      if (sectionKey === 'medications') {{
        const items = (sec.medications && sec.medications.entries) || [];
        if (items.length === 0) {{
          container.innerHTML = '<div class="text-xs text-slate-500 p-4 text-center">No medications in document.</div>';
          return;
        }}
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Medication</th>
              <th class="p-2.5 font-bold">RxNorm</th>
              <th class="p-2.5 font-bold">Dose</th>
              <th class="p-2.5 font-bold">Route</th>
              <th class="p-2.5 font-bold">Schedule</th>
              <th class="p-2.5 font-bold">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        items.forEach(m => {{
          const med = m.medication || {{}};
          const dose = m.dose || {{}};
          const route = m.route || {{}};
          const sched = m.schedule || {{}};
          tableHtml += `<tr class="hover:bg-slate-800/40">
            <td class="p-2.5 font-sans font-semibold text-slate-200">${{escapeHtml(med.display_name || 'N/A')}}</td>
            <td class="p-2.5 text-blue-400">${{escapeHtml(med.code || 'N/A')}}</td>
            <td class="p-2.5 text-emerald-400">${{escapeHtml(dose.formatted || 'N/A')}}</td>
            <td class="p-2.5 text-slate-300 font-sans">${{escapeHtml(route.display_name || 'Oral')}}</td>
            <td class="p-2.5 text-slate-300 font-sans">${{escapeHtml((sched.period && sched.period.human_readable) || 'Standard')}}</td>
            <td class="p-2.5"><span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-sans text-[10px]">${{escapeHtml(m.status || 'active')}}</span></td>
          </tr>`;
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

      }} else if (sectionKey === 'allergies') {{
        const items = (sec.allergies && sec.allergies.entries) || [];
        if (items.length === 0) {{
          container.innerHTML = '<div class="text-xs text-slate-500 p-4 text-center">No allergies in document.</div>';
          return;
        }}
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Substance</th>
              <th class="p-2.5 font-bold">Code</th>
              <th class="p-2.5 font-bold">Severity</th>
              <th class="p-2.5 font-bold">Reactions</th>
              <th class="p-2.5 font-bold">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        items.forEach(a => {{
          const sub = a.substance || {{}};
          const sev = a.severity || {{}};
          const reactions = (a.reactions || []).map(r => (r.reaction && r.reaction.display_name) || '').filter(Boolean).join(', ');
          tableHtml += `<tr class="hover:bg-slate-800/40">
            <td class="p-2.5 font-sans font-semibold text-red-200">${{escapeHtml(sub.display_name || 'N/A')}}</td>
            <td class="p-2.5 text-blue-400">${{escapeHtml(sub.code || 'N/A')}}</td>
            <td class="p-2.5 text-amber-400 font-sans">${{escapeHtml(sev.display_name || 'N/A')}}</td>
            <td class="p-2.5 text-slate-300 font-sans">${{escapeHtml(reactions || 'N/A')}}</td>
            <td class="p-2.5"><span class="px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30 font-sans text-[10px]">${{escapeHtml(a.status || 'active')}}</span></td>
          </tr>`;
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

      }} else if (sectionKey === 'problems') {{
        const items = (sec.problems && sec.problems.entries) || [];
        if (items.length === 0) {{
          container.innerHTML = '<div class="text-xs text-slate-500 p-4 text-center">No problems recorded.</div>';
          return;
        }}
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Problem / Condition</th>
              <th class="p-2.5 font-bold">SNOMED Code</th>
              <th class="p-2.5 font-bold">Onset Date</th>
              <th class="p-2.5 font-bold">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        items.forEach(p => {{
          const prob = p.problem || {{}};
          const onset = typeof p.effective_time === 'string' ? p.effective_time : ((p.effective_time && p.effective_time.low) || 'N/A');
          tableHtml += `<tr class="hover:bg-slate-800/40">
            <td class="p-2.5 font-sans font-semibold text-slate-200">${{escapeHtml(prob.display_name || 'N/A')}}</td>
            <td class="p-2.5 text-purple-400">${{escapeHtml(prob.code || 'N/A')}}</td>
            <td class="p-2.5 text-slate-300">${{escapeHtml(onset)}}</td>
            <td class="p-2.5"><span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-sans text-[10px]">${{escapeHtml(p.status || 'active')}}</span></td>
          </tr>`;
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

      }} else if (sectionKey === 'vitals') {{
        const panels = (sec.vital_signs && sec.vital_signs.panels) || [];
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Measurement</th>
              <th class="p-2.5 font-bold">Value</th>
              <th class="p-2.5 font-bold">Unit</th>
              <th class="p-2.5 font-bold">Interpretation</th>
              <th class="p-2.5 font-bold">Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        panels.forEach(p => {{
          (p.measurements || []).forEach(m => {{
            const vs = m.vital_sign || {{}};
            const val = m.value || {{}};
            const interp = m.interpretation || {{}};
            tableHtml += `<tr class="hover:bg-slate-800/40">
              <td class="p-2.5 font-sans font-semibold text-slate-200">${{escapeHtml(vs.display_name || 'Measurement')}}</td>
              <td class="p-2.5 text-blue-400 font-bold">${{escapeHtml(val.value || '')}}</td>
              <td class="p-2.5 text-slate-400">${{escapeHtml(val.unit || '')}}</td>
              <td class="p-2.5 text-emerald-400 font-sans text-[10px]">${{escapeHtml(interp.display_name || 'Normal')}}</td>
              <td class="p-2.5 text-slate-300">${{escapeHtml(p.date || 'N/A')}}</td>
            </tr>`;
          }});
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

      }} else if (sectionKey === 'labs') {{
        const labs = (sec.results && sec.results.results) || [];
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Diagnostic Test</th>
              <th class="p-2.5 font-bold">LOINC Code</th>
              <th class="p-2.5 font-bold">Result Value</th>
              <th class="p-2.5 font-bold">Unit</th>
              <th class="p-2.5 font-bold">Reference Range</th>
              <th class="p-2.5 font-bold">Interpretation</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        labs.forEach(l => {{
          const test = l.test || {{}};
          const val = l.value || {{}};
          const ref = l.reference_range || {{}};
          const interp = l.interpretation || {{}};
          tableHtml += `<tr class="hover:bg-slate-800/40">
            <td class="p-2.5 font-sans font-semibold text-slate-200">${{escapeHtml(test.display_name || 'Lab Test')}}</td>
            <td class="p-2.5 text-purple-400">${{escapeHtml(test.code || 'N/A')}}</td>
            <td class="p-2.5 text-blue-400 font-bold">${{escapeHtml(val.value || '')}}</td>
            <td class="p-2.5 text-slate-400">${{escapeHtml(val.unit || '')}}</td>
            <td class="p-2.5 text-slate-300">${{escapeHtml(ref.text || (ref.low ? ref.low + ' - ' + ref.high : 'Normal'))}}</td>
            <td class="p-2.5 text-amber-400 font-sans text-[10px]">${{escapeHtml(interp.display_name || 'Normal')}}</td>
          </tr>`;
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

      }} else if (sectionKey === 'immunizations') {{
        const items = (sec.immunizations && sec.immunizations.entries) || [];
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Vaccine</th>
              <th class="p-2.5 font-bold">CVX Code</th>
              <th class="p-2.5 font-bold">Date Given</th>
              <th class="p-2.5 font-bold">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        items.forEach(imm => {{
          const med = imm.medication || {{}};
          tableHtml += `<tr class="hover:bg-slate-800/40">
            <td class="p-2.5 font-sans font-semibold text-slate-200">${{escapeHtml(med.display_name || 'Vaccine')}}</td>
            <td class="p-2.5 text-indigo-400">${{escapeHtml(med.code || 'N/A')}}</td>
            <td class="p-2.5 text-slate-300">${{escapeHtml(imm.date || 'N/A')}}</td>
            <td class="p-2.5"><span class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30 font-sans text-[10px]">${{escapeHtml(imm.status || 'completed')}}</span></td>
          </tr>`;
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

      }} else if (sectionKey === 'encounters') {{
        const items = (sec.encounters && sec.encounters.entries) || [];
        let tableHtml = `<table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-800 bg-slate-900/80 text-slate-300">
              <th class="p-2.5 font-bold">Encounter Description</th>
              <th class="p-2.5 font-bold">Code</th>
              <th class="p-2.5 font-bold">Date</th>
              <th class="p-2.5 font-bold">Location</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono text-[11px]">`;
        items.forEach(e => {{
          const enc = e.encounter || {{}};
          tableHtml += `<tr class="hover:bg-slate-800/40">
            <td class="p-2.5 font-sans font-semibold text-slate-200">${{escapeHtml(enc.display_name || 'Encounter')}}</td>
            <td class="p-2.5 text-blue-400">${{escapeHtml(enc.code || 'N/A')}}</td>
            <td class="p-2.5 text-slate-300">${{escapeHtml(e.date || 'N/A')}}</td>
            <td class="p-2.5 text-slate-300 font-sans">${{escapeHtml(e.location || 'Clinic')}}</td>
          </tr>`;
        }});
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;
      }}
    }}

    // Drag and Drop & File Upload handling
    function handleDragOver(e) {{
      e.preventDefault();
      document.getElementById("dropZoneBanner").classList.add("drag-over-active");
    }}

    function handleDragLeave(e) {{
      e.preventDefault();
      document.getElementById("dropZoneBanner").classList.remove("drag-over-active");
    }}

    function handleFileDrop(e) {{
      e.preventDefault();
      document.getElementById("dropZoneBanner").classList.remove("drag-over-active");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {{
        processLoadedFile(e.dataTransfer.files[0]);
      }}
    }}

    function handleFileSelected(e) {{
      if (e.target && e.target.files && e.target.files.length > 0) {{
        processLoadedFile(e.target.files[0]);
      }}
    }}

    function processLoadedFile(file) {{
      currentFileName = file.name;
      document.getElementById("activeFileName").textContent = file.name;
      const lowerName = file.name.toLowerCase();

      // Read as Text (XML, C-CDA, JSON)
      const reader = new FileReader();
      reader.onload = function(e) {{
        const content = e.target.result;
        if (lowerName.endsWith(".json")) {{
          try {{
            const parsed = JSON.parse(content);
            jsonOutputContent = JSON.stringify(parsed, null, 2);
            updateViewPayloads();
            openInspectorTab("json");
          }} catch (err) {{
            rawInputContent = content;
            updateViewPayloads();
            openInspectorTab("input");
          }}
        }} else {{
          // Load input XML / C-CDA
          rawInputContent = content;
          updateViewPayloads();
          openInspectorTab("input");
        }}
      }};
      reader.readAsText(file);
    }}

    function updateViewPayloads() {{
      const xmlLines = rawInputContent ? rawInputContent.split('\\n').length : 0;
      const jsonLines = jsonOutputContent ? jsonOutputContent.split('\\n').length : 0;
      document.getElementById("inputBadge").textContent = xmlLines + " lines";
      document.getElementById("jsonBadge").textContent = jsonLines + " lines";

      document.getElementById("xmlPayloadArea").innerHTML = "<code>" + escapeHtml(rawInputContent) + "</code>";
      document.getElementById("jsonPayloadArea").innerHTML = "<code>" + escapeHtml(jsonOutputContent) + "</code>";
      document.getElementById("splitXmlArea").innerHTML = "<code>" + escapeHtml(rawInputContent) + "</code>";
      document.getElementById("splitJsonArea").innerHTML = "<code>" + escapeHtml(jsonOutputContent) + "</code>";
    }}
  </script>
</body>
</html>
"""
    return html_content

