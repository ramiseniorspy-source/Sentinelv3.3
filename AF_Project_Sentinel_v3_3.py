import os
import requests
import subprocess
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
BASE_DIR = str(Path(__file__).parent.absolute())
MANIFEST_DIR = Path(__file__).parent / "AF_System_Manifests"
MASTER_LOG = Path(__file__).parent / "AF_MASTER_AUDIT.md"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# Standard Ignore List
IGNORE_EXTENSIONS = {'.safetensors', '.ckpt', '.pt', '.bin', '.pyc', '.git', '.obj', '.exe', '.dll', '.zip'}
SECURITY_KEYWORDS = {'login', 'config', 'env', 'secret', 'pass', 'auth', 'key', 'token', 'exploit', 'payload'}

MANIFEST_DIR.mkdir(exist_ok=True)

def get_gpu_threads():
    try:
        cmd = "powershell \"(Get-CimInstance Win32_VideoController).AdapterRAM / 1GB\""
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        vram = float(output) if output else 2.0
        return 8 if vram >= 15 else (4 if vram >= 7 else 2)
    except: return 2

def print_progress(current, total, prefix=''):
    if total <= 0: return
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled = int(40 * current // total)
    bar = '█' * filled + '-' * (40 - filled)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}%')
    sys.stdout.flush()

def get_recursive_size_gb(path):
    """Accurately calculates total directory size recursively."""
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except: pass
    return round(total_size / (1024**3), 3)

def get_ai_evaluation(name, files, size_gb):
    """Forces AI to use a structured Markdown template."""
    prompt = (
        f"Analyze this project for a technical portfolio: '{name}' ({size_gb} GB).\n"
        f"Files sampled: {files}\n\n"
        f"STRICT FORMATTING RULE: Use headers, bullet points, and double newlines. "
        f"Structure your response exactly like this:\n\n"
        f"## 🔍 Project Overview\n[Brief description of project purpose]\n\n"
        f"## 🛠️ Technical Depth\n* [Key technology 1]\n* [Key technology 2]\n\n"
        f"## 📁 Repository Strategy\n* [Advice on keeping or ignoring this project for GitHub]"
    )
    try:
        res = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}, timeout=45).json().get('response', '')
        return res.strip()
    except: return "## 🔍 Status\nEvaluation Pending (AI Offline)."

def security_audit(project_path):
    """Flags risk levels. Only Severe/High generate full reports."""
    suspicious = []
    try:
        for root, _, files in os.walk(project_path):
            for name in files:
                if any(k in name.lower() for k in SECURITY_KEYWORDS): suspicious.append(name)
            if len(suspicious) > 5: break
    except: pass

    if not suspicious: return "🟢 Clear", ""

    prompt = (
        f"Audit these files in '{project_path.name}': {', '.join(suspicious[:5])}\n"
        f"Determine risk: SEVERE, HIGH, MEDIUM, or LOW.\n"
        f"Respond with: [LEVEL] | [1-sentence reason]"
    )
    try:
        res = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}, timeout=30).json().get('response', '')
        clean_res = res.strip().replace("\n", " ")
        
        is_critical = any(word in clean_res.upper() for word in ['SEVERE', 'HIGH'])
        icon = "🔴" if is_critical else "🟡"
        
        # Only return a detailed report for critical risks
        detailed_report = f"### ⚠️ CRITICAL RISK ALERT\n{clean_res}" if is_critical else ""
        return f"{icon} {clean_res.split('|')[0].strip()}", detailed_report
    except: return "🟡 Unknown", ""

def audit_worker(project):
    eval_text = get_ai_evaluation(project['name'], project['files'], project['size'])
    risk_status, detailed_sec = security_audit(Path(project['path']))
    
    # Write Structured Individual Manifest
    with open(MANIFEST_DIR / f"MANIFEST_{project['name']}.md", "w", encoding="utf-8") as f:
        f.write(f"# 📁 System Audit: {project['name']}\n\n")
        f.write(f"**Location:** `{project['path']}`\n")
        f.write(f"**Total Footprint:** {project['size']} GB\n\n")
        f.write(f"{eval_text}\n\n")
        f.write(f"{detailed_sec}")
    
    return {"name": project['name'], "size": project['size'], "status": risk_status, "sec_report": detailed_sec, "path": project['path']}

def run_v3_3_final_fix():
    threads = get_gpu_threads()
    print(f"--- 🛡️ AF Project Sentinel v3.3 (Executive Audit Mode) ---")
    
    p_dirs = [f for f in Path(BASE_DIR).iterdir() if f.is_dir() and f.name not in ["AF_System_Manifests", "test_folder"]]
    projects = []
    
    for idx, d in enumerate(p_dirs):
        size_gb = get_recursive_size_gb(str(d))
        try:
            files = ", ".join([f.name for f in list(d.iterdir())[:10] if f.is_file()])
        except: files = "Access Denied"
        projects.append({"name": d.name, "path": str(d), "size": size_gb, "files": files})
        print_progress(idx + 1, len(p_dirs), prefix='Mapping ')
    
    print("\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(audit_worker, projects))
        # No progress bar for map in v3.3 to avoid thread-conflict, just completion
        print("Auditing Complete.")

    # MASTER AUDIT (Strict Executive Structure)
    with open(MASTER_LOG, "w", encoding="utf-8") as f:
        f.write(f"# 🛡️ Master Executive Audit: {BASE_DIR}\n\n")
        f.write("## 📊 System Overview\n")
        f.write("| Project Name | Size (GB) | Security Status |\n")
        f.write("|:---|:---:|:---|\n")
        for r in results:
            f.write(f"| {r['name']} | {r['size']} | {r['status']} |\n")
        
        # Security Findings Section - ONLY for Severe/High
        criticals = [r for r in results if r['sec_report']]
        if criticals:
            f.write("\n\n## ⚠️ High-Priority Security Findings\n")
            f.write("The following projects contain SEVERE or HIGH risks that must be resolved before GitHub upload.\n\n")
            for c in criticals:
                f.write(f"### {c['name']}\n{c['sec_report'].replace('### ⚠️ CRITICAL RISK ALERT', '')}\n\n**Path:** `{c['path']}`\n\n---\n")

    print(f"\nMission Complete. Executive Report Ready: {MASTER_LOG}")

if __name__ == "__main__":
    run_v3_3_final_fix()
