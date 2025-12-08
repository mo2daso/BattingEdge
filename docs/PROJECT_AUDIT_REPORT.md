# BattingEdge Project Audit & Organization Report
**Date:** November 30, 2025
**Status:** Post-V8p Production Readiness Check

## 1. Executive Summary
The project has transitioned from experimental research (V1-V7) to a production-ready state (V8p). Currently, the directory contains 28+ mixed notebooks and 12+ model versions. To prepare for deployment and GitHub, we must isolate V8p artifacts and archive approximately 80% of the existing files.

## 2. Notebook Analysis
**Strategy:** Separate the "Golden Path" (V8p training/inference) from historical experiments.

| Category | Action | Criteria | Specific Files Identified |
| :--- | :--- | :--- | :--- |
| **PRODUCTION** | Keep in `notebooks/` | Core pipeline, V8p training, Final Demos | `1_Pose_Estimation_Demo.ipynb`, `2F_Feature_Engineering_V8p.ipynb`, `3_Model_Training_V8p.ipynb`, `Train_V8p_FINAL.ipynb`, `Mids_Defense_Demo.ipynb` |
| **UTILITY** | Move to `notebooks/utils/` | Data counting, helpers, preprocessing | `0_Count_Videos.ipynb`, `0_Utility_*.ipynb` |
| **ARCHIVE** | Move to `archive/old_notebooks/` | Failed attempts, Debug, V1-V7 specific | `V1_Random_Forest_FAIL.ipynb`, `V4_Baby_LSTM.ipynb`, `0_Debug_*.ipynb`, and approx 20 others. |

## 3. Model Inventory
**Strategy:** Retain only the active model chain used in `inference.py`.

| File | Version | Status | Location |
| :--- | :--- | :--- | :--- |
| `shot_model_V8p_best.keras` | V8p | **Active** (Classifier) | `backend/models/` |
| `shot_brain_V8p.keras` | V8p | **Active** (Feature Extractor) | `backend/models/` |
| `shot_encoder_V8p.pkl` | V8p | **Active** (Label Encoder) | `backend/models/` |
| `shot_scaler_V8p.pkl` | V8p | **Active** (StandardScaler) | `backend/models/` |
| `shot_model_V7.keras` | V7 | Obsolete | `archive/old_models/` |
| `error_model_V4.h5` | V4 | Obsolete | `archive/old_models/` |
| *All other checkpoints* | - | Obsolete | `archive/old_models/` |

## 4. Data Organization
**Strategy:** Centralize active data and archive raw/intermediate datasets.

* **Active Training Data:** `data/dataset_v8p/` (Renamed from `dataset_v8_balanced_videos`)
* **Active Features:** `data/features/dataset_v8p/` (103-dim features)
* **Demo Videos:** `data/defense_demos/` (Generated outputs)
* **Testing:** `data/unprofessional_test/` (New uploads)
* **Archived:** `dataset_v7_clean`, `dataset_v7_99feat` move to `archive/old_datasets/`.

## 5. Recommendations
1.  **Immediate Cleanup:** Run `scripts/cleanup_project.py` to enforce this structure.
2.  **Git Ignore:** Update `.gitignore` immediately to prevent committing 2GB+ of archived models.
3.  **Validation:** Run `scripts/test_backend.py` (to be created) after cleanup to ensure path references in `inference.py` are updated.