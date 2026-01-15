"""
BattingEdge V9.5 System Diagnostic Tool
Run this to check your installation before starting tests

Place in ROOT directory and run: python diagnose_system.py
"""
import sys
import os
from pathlib import Path
import importlib.util

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    path = Path(filepath)
    exists = path.exists()
    icon = "✅" if exists else "❌"
    
    if exists:
        size = path.stat().st_size
        size_str = f"({size:,} bytes)" if size < 1024*1024 else f"({size/(1024*1024):.1f} MB)"
        print(f"   {icon} {description:<40s} {size_str}")
    else:
        print(f"   {icon} {description:<40s} MISSING")
    
    return exists

def check_import(module_name):
    """Check if a Python package can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec:
            print(f"   ✅ {module_name:<30s} Installed")
            return True
        else:
            print(f"   ❌ {module_name:<30s} NOT FOUND")
            return False
    except Exception as e:
        print(f"   ❌ {module_name:<30s} ERROR: {e}")
        return False

def main():
    print("=" * 80)
    print("BATTINGEDGE V9.5 - SYSTEM DIAGNOSTIC")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    # ===== CHECK 1: Project Structure =====
    print("\n📁 CHECK 1: Project Structure")
    print("-" * 80)
    
    required_files = [
        ("backend/main.py", "FastAPI Server"),
        ("backend/inference.py", "Ensemble Classifier"),
        ("backend/database.py", "Database Operations"),
        ("backend/shot_rules.py", "Grading System"),
        ("backend/report.py", "PDF Generation"),
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            errors.append(f"Missing required file: {filepath}")
    
    # ===== CHECK 2: Model Files =====
    print("\n🤖 CHECK 2: Model Files")
    print("-" * 80)
    
    model_files = [
        ("backend/models/scaler_V9_5.pkl", "Feature Scaler"),
        ("backend/models/classes_V9_5.pkl", "Class Labels"),
        ("backend/models/battingedge_V9_5_best.keras", "BiLSTM Model"),
        ("backend/models/battingedge_V9_5_xgboost_best.json", "XGBoost Model"),
        ("backend/models/battingedge_V9_5_random_forest_best.pkl", "Random Forest Model"),
        ("backend/models/battingedge_V9_5_meta_model.pkl", "Meta-Learner Model"),
    ]
    
    for filepath, description in model_files:
        if not check_file_exists(filepath, description):
            errors.append(f"Missing model file: {filepath}")
    
    # ===== CHECK 3: Python Dependencies =====
    print("\n🐍 CHECK 3: Python Dependencies")
    print("-" * 80)
    
    dependencies = [
        "fastapi", "uvicorn", "aiofiles", "tensorflow", "xgboost", 
        "sklearn", "cv2", "mediapipe", "numpy", "reportlab"
    ]
    
    for dep in dependencies:
        if not check_import(dep):
            errors.append(f"Missing Python package: {dep}")
    
    # ===== CHECK 4: Backend Import Test =====
    print("\n⚙️  CHECK 4: Backend Import Test")
    print("-" * 80)
    
    backend_path = Path(__file__).parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    backend_modules = [
        ("inference", "StackingEnsembleClassifier"),
        ("database", "Database operations"),
        ("shot_rules", "ShotRules grading"),
        ("report", "PDF generation"),
    ]
    
    for module_name, description in backend_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name:<30s} Imports successfully")
        except Exception as e:
            print(f"   ❌ {module_name:<30s} IMPORT ERROR: {e}")
            errors.append(f"Cannot import {module_name}: {e}")
    
    # ===== CHECK 5: Model Loading Test =====
    print("\n🧠 CHECK 5: Model Loading Test")
    print("-" * 80)
    
    try:
        from inference import StackingEnsembleClassifier
        print("   ⏳ Loading model...")
        classifier = StackingEnsembleClassifier()
        
        if classifier.is_ensemble:
            print(f"   ✅ Ensemble model loaded successfully")
            print(f"   ✅ Mode: Stacking Ensemble (BiLSTM+XGBoost+RF)")
        else:
            print(f"   ⚠️  Loaded BiLSTM only (fallback mode)")
            warnings.append("Ensemble models not loading - using BiLSTM fallback")
    except Exception as e:
        print(f"   ❌ Model loading FAILED: {e}")
        errors.append(f"Cannot load model: {e}")
    
    # ===== CHECK 6: Database Test =====
    print("\n💾 CHECK 6: Database Test")
    print("-" * 80)
    
    try:
        import database as db
        db.init_db()
        print(f"   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Database test FAILED: {e}")
        errors.append(f"Database error: {e}")
    
    # ===== SUMMARY =====
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if not errors and not warnings:
        print("\n✅ ALL CHECKS PASSED!")
        print("\n   Your system is ready. Run 'python test_full_system.py' next.")
    else:
        if errors:
            print(f"\n❌ ERRORS FOUND ({len(errors)}):")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")
        
        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()