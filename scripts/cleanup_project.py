import os
import shutil
import glob
from pathlib import Path
import sys

# ==========================================
# CONFIGURATION
# ==========================================
# Base directory (assumes script is run from project root or scripts folder)
BASE_DIR = Path(__file__).resolve().parent.parent
DRY_RUN = True  # Set to False to actually move files

# Structure Definition
DIRS_TO_CREATE = [
    'backend/models',
    'backend/uploads',
    'backend/outputs',
    'frontend/public',
    'frontend/src',
    'data/dataset_v8p',
    'data/features/dataset_v8p',
    'data/defense_demos',
    'data/unprofessional_test',
    'tests/unprofessional_test_results',
    'tests/validation_results',
    'docs/reports',
    'docs/presentation/Screenshots',
    'notebooks/utils',
    'scripts',
    'archive/old_notebooks',
    'archive/old_models',
    'archive/old_datasets',
    'archive/old_reports'
]

# File Rules (Filename partial matches or full names)
KEEP_NOTEBOOKS = [
    '1_Pose_Estimation', 'Feature_Engineering_V8p', 'Model_Training_V8p',
    'Train_V8p_FINAL', 'Mids_Defense', 'Defense_Demo'
]
UTIL_NOTEBOOKS = ['0_Count_Videos', '0_Utility']

KEEP_MODELS = [
    'shot_model_V8p_best.keras', 'shot_brain_V8p.keras',
    'shot_encoder_V8p.pkl', 'shot_scaler_V8p.pkl'
]

ACTIVE_DATASETS = ['dataset_v8_balanced_videos', 'dataset_v8p']

# ==========================================
# UTILITY FUNCTIONS
# ==========================================
def log(msg, level="INFO"):
    prefix = "[TEST]" if DRY_RUN else "[ACTION]"
    print(f"{prefix} {msg}")

def safe_move(src, dst):
    if not os.path.exists(src):
        return
    
    if DRY_RUN:
        log(f"Would move: {src.name} -> {dst}")
    else:
        try:
            shutil.move(str(src), str(dst))
            log(f"Moved: {src.name} -> {dst}")
        except Exception as e:
            log(f"ERROR moving {src.name}: {e}", "ERROR")

def update_gitignore():
    gitignore_content = """
# Data
*.mp4
*.avi
*.npy
data/dataset_v8p/
data/features/
archive/

# Models (exclude V8p production models if small enough, else ignore all)
backend/models/*.keras
backend/models/*.h5
!backend/models/shot_model_V8p_best.keras
!backend/models/shot_encoder_V8p.pkl
!backend/models/shot_scaler_V8p.pkl

# Backend
backend/uploads/
backend/outputs/
__pycache__/
*.pyc
venv/
.env

# Frontend
frontend/node_modules/
frontend/build/

# IDE/OS
.vscode/
.idea/
.DS_Store
Thumbs.db
"""
    path = BASE_DIR / ".gitignore"
    if DRY_RUN:
        log("Would update .gitignore")
    else:
        with open(path, "w") as f:
            f.write(gitignore_content.strip())
        log("Updated .gitignore")

# ==========================================
# MAIN LOGIC
# ==========================================
def main():
    print(f"🚀 STARTING CLEANUP (DRY_RUN={DRY_RUN})")
    print(f"📂 Root: {BASE_DIR}")
    
    # 1. Create Directories
    for d in DIRS_TO_CREATE:
        path = BASE_DIR / d
        if not path.exists():
            if DRY_RUN:
                log(f"Would create dir: {d}")
            else:
                path.mkdir(parents=True, exist_ok=True)
                log(f"Created dir: {d}")

    # 2. Organize Notebooks
    notebooks_dir = BASE_DIR / "notebooks"
    if notebooks_dir.exists():
        for nb in notebooks_dir.glob("*.ipynb"):
            name = nb.name
            
            # Utils
            if any(x in name for x in UTIL_NOTEBOOKS):
                safe_move(nb, BASE_DIR / "notebooks/utils" / name)
            # Production
            elif any(x in name for x in KEEP_NOTEBOOKS):
                log(f"Keeping Production Notebook: {name}")
                pass # Already in notebooks/
            # Archive everything else
            else:
                safe_move(nb, BASE_DIR / "archive/old_notebooks" / name)

    # 3. Organize Models
    # Scan root and backend/models for loose files
    possible_locs = [BASE_DIR, BASE_DIR / "backend/models"]
    for loc in possible_locs:
        if not loc.exists(): continue
        for ext in ['*.keras', '*.h5', '*.pkl']:
            for model_file in loc.glob(ext):
                name = model_file.name
                
                # Production V8p
                if name in KEEP_MODELS:
                    # Ensure it is in backend/models
                    target = BASE_DIR / "backend/models" / name
                    if model_file != target:
                        safe_move(model_file, target)
                    else:
                        log(f"Keeping Production Model: {name}")
                # Archive
                else:
                    safe_move(model_file, BASE_DIR / "archive/old_models" / name)

    # 4. Organize Data
    data_dir = BASE_DIR / "data"
    if data_dir.exists():
        for item in data_dir.iterdir():
            if item.is_dir():
                name = item.name
                if name == "dataset_v8_balanced_videos":
                    # Rename to standard v8p name
                    target = data_dir / "dataset_v8p"
                    if DRY_RUN:
                        log(f"Would rename {name} to dataset_v8p")
                    else:
                        if not target.exists():
                            item.rename(target)
                            log(f"Renamed {name} -> dataset_v8p")
                elif name in ["dataset_v8p", "features", "demo_videos", "defense_demos", "unprofessional_test"]:
                    log(f"Keeping Data Dir: {name}")
                else:
                    # Archive old datasets (v7, v6, etc)
                    safe_move(item, BASE_DIR / "archive/old_datasets" / name)

    # 5. Organize Results & Reports
    # Move CSVs
    for csv in BASE_DIR.glob("*.csv"):
        if "test_results" in csv.name:
            safe_move(csv, BASE_DIR / "tests" / csv.name)
    
    # Move PDFs
    for pdf in BASE_DIR.glob("*.pdf"):
        safe_move(pdf, BASE_DIR / "docs/reports" / pdf.name)

    # 6. Update Gitignore
    update_gitignore()

    print("\n✅ CLEANUP SCAN COMPLETE")
    if DRY_RUN:
        print("⚠️  This was a DRY RUN. No files were moved.")
        print("👉 Set DRY_RUN = False in the script to execute.")

if __name__ == "__main__":
    main()