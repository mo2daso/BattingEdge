import os
import json
import datetime
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = "."
IGNORE_DIRS = {'.git', 'venv', 'node_modules', '__pycache__', '.idea', '.vscode'}
IGNORE_EXTS = {'.pyc'}

# --- DATA STRUCTURES ---
audit_data = {
    "summary": {"total_size_mb": 0, "file_count": 0, "empty_folders": []},
    "models": [],       # .pt, .keras, .h5, .pkl
    "datasets": [],     # Folders in 'data'
    "notebooks": [],    # .ipynb
    "scripts": [],      # .py
    "logs_and_tmp": [], # .log, .txt inside logs
    "large_files": [],  # > 100MB
    "structure": {}
}

def get_size_mb(path):
    try:
        return os.path.getsize(path) / (1024 * 1024)
    except OSError:
        return 0

def get_mod_time(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')

def read_head(path, lines=3):
    """Reads the first few lines to understand file intent."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f.readlines()[:lines] if line.strip()]
    except:
        return ["(Binary or unreadable content)"]

print("🔍 Starting Deep Audit... this might take a minute...")

for root, dirs, files in os.walk(ROOT_DIR):
    # Filter ignored directories in-place
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    
    # Check for empty folders
    if not dirs and not files:
        audit_data["summary"]["empty_folders"].append(root)

    for file in files:
        file_path = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        
        if ext in IGNORE_EXTS:
            continue

        size_mb = get_size_mb(file_path)
        mod_time = get_mod_time(file_path)
        audit_data["summary"]["total_size_mb"] += size_mb
        audit_data["summary"]["file_count"] += 1

        file_info = {
            "path": file_path,
            "name": file,
            "size_mb": round(size_mb, 2),
            "modified": mod_time
        }

        # CATEGORIZATION
        if size_mb > 50:
            audit_data["large_files"].append(file_info)

        if ext in ['.pt', '.keras', '.h5', '.pkl', '.onnx', '.npy']:
            audit_data["models"].append(file_info)
        elif ext == '.ipynb':
            audit_data["notebooks"].append(file_info)
        elif ext == '.py':
            # Add content preview for scripts
            file_info['preview'] = read_head(file_path)
            audit_data["scripts"].append(file_info)
        elif "dataset" in root.lower() or "data" in root.lower():
             # roughly categorizing data files if not caught above
             pass
        elif "log" in root.lower() or ext == '.log':
            audit_data["logs_and_tmp"].append(file_info)

# --- GENERATE REPORT ---
report_lines = []
report_lines.append(f"# BATTING EDGE PROJECT AUDIT REPORT")
report_lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append(f"Total Size: {round(audit_data['summary']['total_size_mb'], 2)} MB")
report_lines.append("-" * 40)

report_lines.append("\n## 1. HEAVY FILES (Candidates for deletion/Git LFS)")
for item in sorted(audit_data["large_files"], key=lambda x: x['size_mb'], reverse=True):
    report_lines.append(f"- [{item['size_mb']} MB] {item['path']} ({item['modified']})")

report_lines.append("\n## 2. MODEL FILES (Keep only the best V8p/Final)")
for item in sorted(audit_data["models"], key=lambda x: x['modified'], reverse=True):
    report_lines.append(f"- {item['name']} | {item['size_mb']} MB | Path: {item['path']}")

report_lines.append("\n## 3. PYTHON SCRIPTS (Check for duplicates)")
for item in sorted(audit_data["scripts"], key=lambda x: x['path']):
    report_lines.append(f"- {item['path']}")
    if 'preview' in item:
        report_lines.append(f"  Preview: {item['preview']}")

report_lines.append("\n## 4. EMPTY FOLDERS (Safe to delete)")
for folder in audit_data["summary"]["empty_folders"]:
    report_lines.append(f"- {folder}")

# Save to file
with open("DEEP_AUDIT_SUMMARY.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

# Save raw JSON for the cleanup script to use later
with open("audit_data.json", "w", encoding="utf-8") as f:
    json.dump(audit_data, f, indent=4)

print("✅ Audit Complete.")
print("👉 Open 'DEEP_AUDIT_SUMMARY.md' and read it.")