"""
BattingEdge Project Audit Script
Analyzes entire project structure and creates detailed inventory
"""

import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class ProjectAuditor:
    def __init__(self, project_root='.'):
        self.project_root = Path(project_root)
        self.inventory = {
            'notebooks': [],
            'models': [],
            'datasets': [],
            'features': [],
            'videos': [],
            'results': [],
            'reports': [],
            'images': [],
            'python_files': [],
            'other': []
        }
        self.total_size = 0
        
    def human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def analyze_notebook(self, filepath):
        """Analyze Jupyter notebook"""
        name = filepath.name
        size = filepath.stat().st_size
        modified = datetime.fromtimestamp(filepath.stat().st_mtime)
        
        # Categorize notebook
        category = 'unknown'
        status = 'unknown'
        
        if 'FAIL' in name or 'fail' in name:
            category = 'failed_experiment'
            status = 'archive'
        elif 'Debug' in name or 'debug' in name:
            category = 'debug'
            status = 'archive'
        elif 'Test' in name or 'test' in name:
            category = 'testing'
            status = 'archive'
        elif 'Utility' in name or 'Count' in name:
            category = 'utility'
            status = 'keep_utils'
        elif 'Feature_Engineering' in name and 'V8' in name:
            category = 'production_feature'
            status = 'keep_main'
        elif 'Training' in name and 'V8' in name:
            category = 'production_training'
            status = 'keep_main'
        elif 'Pose_Estimation' in name:
            category = 'demo'
            status = 'keep_main'
        elif 'Defense' in name or 'Mids' in name:
            category = 'defense'
            status = 'keep_main'
        elif any(v in name for v in ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']):
            category = 'old_version'
            status = 'archive'
        else:
            category = 'needs_review'
            status = 'review'
        
        return {
            'path': str(filepath.relative_to(self.project_root)),
            'name': name,
            'size': self.human_readable_size(size),
            'size_bytes': size,
            'modified': modified.strftime('%Y-%m-%d %H:%M'),
            'category': category,
            'status': status
        }
    
    def analyze_model(self, filepath):
        """Analyze model file"""
        name = filepath.name
        size = filepath.stat().st_size
        
        # Determine version and purpose
        if 'V8p' in name:
            version = 'V8p'
            status = 'keep_production'
        elif any(v in name for v in ['V7', 'V6', 'V5', 'V4', 'V3', 'V2', 'V1']):
            version = name.split('V')[1].split('_')[0] if 'V' in name else 'unknown'
            status = 'archive'
        else:
            version = 'unknown'
            status = 'review'
        
        model_type = 'unknown'
        if 'shot' in name.lower():
            model_type = 'shot_classifier'
        elif 'error' in name.lower():
            model_type = 'error_detector'
        elif 'scaler' in name.lower():
            model_type = 'scaler'
        elif 'encoder' in name.lower():
            model_type = 'encoder'
        
        return {
            'path': str(filepath.relative_to(self.project_root)),
            'name': name,
            'size': self.human_readable_size(size),
            'size_bytes': size,
            'version': version,
            'type': model_type,
            'status': status
        }
    
    def analyze_dataset(self, dirpath):
        """Analyze dataset folder"""
        video_count = 0
        total_size = 0
        
        for ext in ['*.mp4', '*.avi', '*.mov']:
            videos = list(dirpath.rglob(ext))
            video_count += len(videos)
            total_size += sum(v.stat().st_size for v in videos)
        
        name = dirpath.name
        
        # Determine status
        if 'v8' in name.lower() and 'balanced' in name.lower():
            status = 'keep_active'
            version = 'V8p'
        elif 'v8' in name.lower():
            status = 'keep_active'
            version = 'V8'
        elif 'v7' in name.lower():
            status = 'archive'
            version = 'V7'
        elif 'unprofessional' in name.lower():
            status = 'keep_test'
            version = 'test'
        elif 'demo' in name.lower() or 'defense' in name.lower():
            status = 'keep_demo'
            version = 'demo'
        else:
            status = 'review'
            version = 'unknown'
        
        return {
            'path': str(dirpath.relative_to(self.project_root)),
            'name': name,
            'video_count': video_count,
            'size': self.human_readable_size(total_size),
            'size_bytes': total_size,
            'version': version,
            'status': status
        }
    
    def analyze_features(self, dirpath):
        """Analyze feature folder"""
        npy_files = list(dirpath.rglob('*.npy'))
        npy_count = len(npy_files)
        total_size = sum(f.stat().st_size for f in npy_files)
        
        name = dirpath.name
        
        if 'v8p' in name.lower():
            status = 'keep_active'
            version = 'V8p'
            features = '103-dim'
        elif 'v7' in name.lower():
            status = 'archive'
            version = 'V7'
            features = '66-dim or 99-dim'
        else:
            status = 'review'
            version = 'unknown'
            features = 'unknown'
        
        return {
            'path': str(dirpath.relative_to(self.project_root)),
            'name': name,
            'npy_count': npy_count,
            'size': self.human_readable_size(total_size),
            'size_bytes': total_size,
            'version': version,
            'features': features,
            'status': status
        }
    
    def scan_project(self):
        """Main scanning function"""
        print("🔍 Scanning project structure...")
        print(f"📁 Project root: {self.project_root.absolute()}\n")
        
        # Scan for notebooks
        print("📓 Scanning notebooks...")
        for nb in self.project_root.rglob('*.ipynb'):
            if '.ipynb_checkpoints' not in str(nb):
                info = self.analyze_notebook(nb)
                self.inventory['notebooks'].append(info)
                self.total_size += info['size_bytes']
        
        # Scan for models
        print("🧠 Scanning model files...")
        for ext in ['*.keras', '*.h5', '*.pkl']:
            for model in self.project_root.rglob(ext):
                info = self.analyze_model(model)
                self.inventory['models'].append(info)
                self.total_size += info['size_bytes']
        
        # Scan for datasets (video folders)
        print("🎥 Scanning datasets...")
        dataset_folders = set()
        for video in self.project_root.rglob('*.mp4'):
            dataset_folders.add(video.parent)
        for video in self.project_root.rglob('*.avi'):
            dataset_folders.add(video.parent)
        
        for folder in dataset_folders:
            if 'dataset' in folder.name.lower() or 'demo' in folder.name.lower() or 'unprofessional' in folder.name.lower():
                info = self.analyze_dataset(folder)
                self.inventory['datasets'].append(info)
                self.total_size += info['size_bytes']
        
        # Scan for feature folders
        print("📊 Scanning feature files...")
        for folder in self.project_root.rglob('*'):
            if folder.is_dir() and any(folder.rglob('*.npy')):
                if 'feature' in folder.name.lower() or 'feat' in folder.name.lower() or any(p.name == 'features' for p in folder.parents):
                    info = self.analyze_features(folder)
                    self.inventory['features'].append(info)
                    self.total_size += info['size_bytes']
        
        # Scan for results
        print("📈 Scanning result files...")
        for csv in self.project_root.rglob('*.csv'):
            if 'result' in csv.name.lower() or 'test' in csv.name.lower():
                size = csv.stat().st_size
                self.inventory['results'].append({
                    'path': str(csv.relative_to(self.project_root)),
                    'name': csv.name,
                    'size': self.human_readable_size(size),
                    'modified': datetime.fromtimestamp(csv.stat().st_mtime).strftime('%Y-%m-%d')
                })
        
        # Scan for reports and images
        print("📄 Scanning reports and images...")
        for pdf in self.project_root.rglob('*.pdf'):
            size = pdf.stat().st_size
            self.inventory['reports'].append({
                'path': str(pdf.relative_to(self.project_root)),
                'name': pdf.name,
                'size': self.human_readable_size(size)
            })
        
        for img in self.project_root.rglob('*.png'):
            self.inventory['images'].append(str(img.relative_to(self.project_root)))
        for img in self.project_root.rglob('*.jpg'):
            self.inventory['images'].append(str(img.relative_to(self.project_root)))
        
        # Scan for Python files
        print("🐍 Scanning Python files...")
        for py in self.project_root.rglob('*.py'):
            if '__pycache__' not in str(py) and 'venv' not in str(py):
                size = py.stat().st_size
                self.inventory['python_files'].append({
                    'path': str(py.relative_to(self.project_root)),
                    'name': py.name,
                    'size': self.human_readable_size(size)
                })
        
        print("\n✅ Scan complete!\n")
    
    def generate_report(self):
        """Generate detailed report"""
        report = []
        report.append("=" * 80)
        report.append("BATTINGEDGE PROJECT AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Project Size: {self.human_readable_size(self.total_size)}")
        report.append("=" * 80)
        report.append("")
        
        # Notebooks summary
        report.append("📓 NOTEBOOKS SUMMARY")
        report.append("-" * 80)
        report.append(f"Total notebooks: {len(self.inventory['notebooks'])}")
        
        status_counts = {}
        for nb in self.inventory['notebooks']:
            status = nb['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            report.append(f"  - {status}: {count} notebooks")
        report.append("")
        
        # Group notebooks by status
        for status in ['keep_main', 'keep_utils', 'archive', 'review']:
            nbs = [nb for nb in self.inventory['notebooks'] if nb['status'] == status]
            if nbs:
                report.append(f"\n{status.upper().replace('_', ' ')}:")
                for nb in sorted(nbs, key=lambda x: x['name']):
                    report.append(f"  ✓ {nb['name']}")
                    report.append(f"    Path: {nb['path']}")
                    report.append(f"    Size: {nb['size']}, Modified: {nb['modified']}")
                    report.append(f"    Category: {nb['category']}")
        
        report.append("\n" + "=" * 80)
        
        # Models summary
        report.append("\n🧠 MODELS SUMMARY")
        report.append("-" * 80)
        report.append(f"Total model files: {len(self.inventory['models'])}")
        
        production_models = [m for m in self.inventory['models'] if m['status'] == 'keep_production']
        archive_models = [m for m in self.inventory['models'] if m['status'] == 'archive']
        
        report.append(f"  - Production (V8p): {len(production_models)} files")
        report.append(f"  - Archive (V1-V7): {len(archive_models)} files")
        report.append("")
        
        if production_models:
            report.append("PRODUCTION MODELS (KEEP):")
            for m in production_models:
                report.append(f"  ✓ {m['name']}")
                report.append(f"    Path: {m['path']}")
                report.append(f"    Size: {m['size']}, Type: {m['type']}")
        
        if archive_models:
            report.append("\nOLD MODELS (ARCHIVE):")
            for m in sorted(archive_models, key=lambda x: x['version']):
                report.append(f"  📦 {m['name']} (Version: {m['version']}, Size: {m['size']})")
        
        report.append("\n" + "=" * 80)
        
        # Datasets summary
        report.append("\n🎥 DATASETS SUMMARY")
        report.append("-" * 80)
        
        for dataset in self.inventory['datasets']:
            status_icon = "✓" if dataset['status'] == 'keep_active' else "📦" if dataset['status'] == 'archive' else "🔍"
            report.append(f"\n{status_icon} {dataset['name']} [{dataset['status'].upper()}]")
            report.append(f"   Path: {dataset['path']}")
            report.append(f"   Videos: {dataset['video_count']}")
            report.append(f"   Size: {dataset['size']}")
            report.append(f"   Version: {dataset['version']}")
        
        report.append("\n" + "=" * 80)
        
        # Features summary
        report.append("\n📊 FEATURES SUMMARY")
        report.append("-" * 80)
        
        for feat in self.inventory['features']:
            status_icon = "✓" if feat['status'] == 'keep_active' else "📦"
            report.append(f"\n{status_icon} {feat['name']} [{feat['status'].upper()}]")
            report.append(f"   Path: {feat['path']}")
            report.append(f"   NPY files: {feat['npy_count']}")
            report.append(f"   Size: {feat['size']}")
            report.append(f"   Features: {feat['features']}")
        
        report.append("\n" + "=" * 80)
        
        # Results summary
        if self.inventory['results']:
            report.append("\n📈 RESULTS FILES")
            report.append("-" * 80)
            for res in self.inventory['results']:
                report.append(f"  • {res['name']}")
                report.append(f"    Path: {res['path']}")
                report.append(f"    Size: {res['size']}, Modified: {res['modified']}")
        
        # Reports and images
        if self.inventory['reports']:
            report.append("\n📄 REPORT FILES (PDF)")
            report.append("-" * 80)
            for rep in self.inventory['reports']:
                report.append(f"  • {rep['name']} ({rep['size']})")
                report.append(f"    Path: {rep['path']}")
        
        if self.inventory['images']:
            report.append("\n🖼️ IMAGE FILES")
            report.append("-" * 80)
            report.append(f"Total images: {len(self.inventory['images'])}")
            for img in self.inventory['images'][:10]:  # Show first 10
                report.append(f"  • {img}")
            if len(self.inventory['images']) > 10:
                report.append(f"  ... and {len(self.inventory['images']) - 10} more")
        
        # Python files
        if self.inventory['python_files']:
            report.append("\n🐍 PYTHON FILES")
            report.append("-" * 80)
            for py in self.inventory['python_files']:
                report.append(f"  • {py['name']}")
                report.append(f"    Path: {py['path']}")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename='PROJECT_AUDIT_REPORT.txt'):
        """Save report to file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Report saved to: {filename}")
        return report
    
    def save_json(self, filename='project_inventory.json'):
        """Save inventory as JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.inventory, f, indent=2)
        print(f"✅ JSON inventory saved to: {filename}")


if __name__ == "__main__":
    print("🚀 Starting BattingEdge Project Audit...\n")
    
    auditor = ProjectAuditor('.')
    auditor.scan_project()
    
    # Print report to console
    report = auditor.generate_report()
    print(report)
    
    # Save to files
    auditor.save_report('PROJECT_AUDIT_REPORT.txt')
    auditor.save_json('project_inventory.json')
    
    print("\n✨ Audit complete! Review the report and run cleanup script next.")