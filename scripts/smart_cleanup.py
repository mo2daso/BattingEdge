import os
import shutil
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
SOURCE_DIR = Path(".")
BACKUP_ROOT = Path(r"D:\Users\Anoshia\FYP\Old Files")

# Timestamp to keep backups unique
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M")
CURRENT_BACKUP_DIR = BACKUP_ROOT / f"Cleanup_{TIMESTAMP}"

# --- 1. DESTINATION FOLDERS (Where things go in the backup) ---
DESTINATIONS = {
    "datasets": CURRENT_BACKUP_DIR / "01_Legacy_Datasets",
    "models":   CURRENT_BACKUP_DIR / "02_Deprecated_Models",
    "videos":   CURRENT_BACKUP_DIR / "03_Future_Work_Videos",
    "logs":     CURRENT_BACKUP_DIR / "04_Logs_and_Cache",
    "reports":  CURRENT_BACKUP_DIR / "05_Audit_Reports",
    "misc":     CURRENT_BACKUP_DIR / "06_Misc_Unused",
}

# --- 2. THE MASTER LIST (Source -> Category -> New Name) ---
# If "rename_to" is None, it keeps the original name.
# If "rename_to" has a string, it RENAMES the file/folder in the backup.

MOVE_TASKS = [
    # --- VIDEOS (Renaming for clarity) ---
    {
        "src": r"data\raw_test_clips", 
        "cat": "videos", 
        "rename_to": "Raw_Testing_Clips_Unsorted"  # Renamed from raw_test_clips
    },

    # --- DATASETS (Archiving V7) ---
    {
        "src": r"data\features\dataset_v7_99feat", 
        "cat": "datasets", 
        "rename_to": "V7_Extracted_Features"
    },
    {
        "src": r"data\dataset_v7_clean", 
        "cat": "datasets", 
        "rename_to": "V7_Raw_Video_Dataset"
    },

    # --- MODELS (Archiving Old Versions) ---
    {"src": r"backend\models\base_model_V7_BRAIN.keras", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_model_V7.keras", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_encoder_V7.pkl", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_scaler_V7.pkl", "cat": "models", "rename_to": None},
    
    # Archiving V8 (Since V8p is your final)
    {"src": r"backend\models\shot_brain_V8.keras", "cat": "models", "rename_to": "shot_brain_V8_Legacy.keras"},
    {"src": r"backend\models\shot_model_V8_final.keras", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_model_V8_best.keras", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_encoder_V8.pkl", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_scaler_V8.pkl", "cat": "models", "rename_to": None},
    {"src": r"backend\models\shot_model_DIAGNOSTIC.keras", "cat": "models", "rename_to": "Diagnostic_Model_Archived.keras"},

    # --- LOGS & JUNK ---
    {"src": r"logs", "cat": "logs", "rename_to": "Old_Project_Logs"},
    {"src": r"__pycache__", "cat": "logs", "rename_to": "Root_Pycache"},
    {"src": r"backend\__pycache__", "cat": "logs", "rename_to": "Backend_Pycache"},
    {"src": r"backend\models\checkpoints", "cat": "logs", "rename_to": "Unused_Checkpoints"},

    # --- MISC & EMPTY ---
    {"src": r"data\plots", "cat": "misc", "rename_to": "Generated_Plots_Archive"},
    {"src": r"frontend", "cat": "misc", "rename_to": "Unused_Frontend_Structure"},

    # --- AUDIT REPORTS (Move the reports we just made) ---
    {"src": r"DEEP_AUDIT_SUMMARY.md", "cat": "reports", "rename_to": f"Audit_Report_{TIMESTAMP}.md"},
    {"src": r"audit_data.json", "cat": "reports", "rename_to": f"Audit_Data_{TIMESTAMP}.json"},
    {"src": r"deep_audit.py", "cat": "reports", "rename_to": "Source_Audit_Script.py"},
]

def perform_smart_cleanup():
    print(f"🚀 Starting Smart Cleanup & Archive...")
    print(f"📂 Backup Target: {CURRENT_BACKUP_DIR}")
    print("-" * 60)

    # 1. Create Destination Folders
    for key, path in DESTINATIONS.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Error creating folder {path}: {e}")
            return

    moved_count = 0

    # 2. Execute The Task List
    for task in MOVE_TASKS:
        src_path = SOURCE_DIR / task["src"]
        category = task["cat"]
        new_name = task["rename_to"]
        
        dest_folder = DESTINATIONS[category]

        if src_path.exists():
            # Determine final name
            final_name = new_name if new_name else src_path.name
            dest_path = dest_folder / final_name

            try:
                shutil.move(str(src_path), str(dest_path))
                
                # Visual feedback for renaming
                if new_name:
                    print(f"✅ MOVED & RENAMED: {src_path.name} \n   -> {category}/{final_name}")
                else:
                    print(f"✅ MOVED: {src_path.name} -> {category}/")
                
                moved_count += 1
            except Exception as e:
                print(f"⚠️ Failed to move {src_path.name}: {e}")
        else:
            # File already gone or doesn't exist
            pass

    # 3. Handle Duplicate YOLOv8 (Special Logic)
    # Goal: Ensure ONE copy is in backend/models, archive others.
    
    yolo_root = SOURCE_DIR / "yolov8n.pt"
    yolo_nb = SOURCE_DIR / "notebooks" / "yolov8n.pt"
    yolo_backend = SOURCE_DIR / "backend" / "models" / "yolov8n.pt"
    
    print("-" * 60)
    print("🔍 Checking for Duplicate Models...")

    # Case A: If backend has it, root/notebook copies are duplicates -> Archive them
    if yolo_backend.exists():
        if yolo_root.exists():
            shutil.move(str(yolo_root), str(DESTINATIONS["misc"] / "yolov8n_root_duplicate.pt"))
            print("✅ Archived duplicate yolov8n.pt found in Root")
        if yolo_nb.exists():
            shutil.move(str(yolo_nb), str(DESTINATIONS["misc"] / "yolov8n_notebook_duplicate.pt"))
            print("✅ Archived duplicate yolov8n.pt found in Notebooks")
            
    # Case B: Backend doesn't have it, but Root does -> Move Root copy to Backend (Don't archive)
    elif yolo_root.exists():
        shutil.move(str(yolo_root), str(yolo_backend))
        print("📦 Moved yolov8n.pt from Root to backend/models/ (Consolidating)")
        # If notebook also had it, archive that one
        if yolo_nb.exists():
            shutil.move(str(yolo_nb), str(DESTINATIONS["misc"] / "yolov8n_notebook_duplicate.pt"))
            print("✅ Archived duplicate yolov8n.pt found in Notebooks")

    print("-" * 60)
    print(f"🎉 SUCCESS! Moved {moved_count} items to backup.")
    print(f"👉 Location: {CURRENT_BACKUP_DIR}")
    print("👉 You can now run 'git init', 'git add .', and 'git commit'.")

if __name__ == "__main__":
    perform_smart_cleanup()