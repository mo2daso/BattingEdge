import os
import json
from pathlib import Path
from collections import defaultdict

class ProjectDiagnostic:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.large_files = []
        self.file_types = defaultdict(list)
        self.total_size = 0
        self.excluded_patterns = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
            'env', '.idea', '.vscode', 'dist', 'build'
        }
        self.suspicious_extensions = {
            # Models
            '.h5', '.pt', '.pth', '.ckpt', '.pb', '.onnx', '.tflite', '.pkl', '.joblib',
            # Videos
            '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm',
            # Large data
            '.csv', '.parquet', '.hdf5', '.npy', '.npz',
            # Images (large collections)
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            # Audio
            '.mp3', '.wav', '.flac', '.ogg',
            # Archives
            '.zip', '.tar', '.gz', '.rar', '.7z',
            # Database
            '.db', '.sqlite', '.sqlite3',
            # Other
            '.exe', '.dll', '.so', '.dylib'
        }
    
    def get_size_mb(self, size_bytes):
        return size_bytes / (1024 * 1024)
    
    def should_skip(self, path):
        parts = path.parts
        return any(excluded in parts for excluded in self.excluded_patterns)
    
    def scan_directory(self):
        print(f"Scanning directory: {self.root}")
        print("=" * 80)
        
        for item in self.root.rglob('*'):
            if self.should_skip(item):
                continue
            
            if item.is_file():
                try:
                    size = item.stat().st_size
                    self.total_size += size
                    ext = item.suffix.lower()
                    rel_path = item.relative_to(self.root)
                    
                    self.file_types[ext].append({
                        'path': str(rel_path),
                        'size': size
                    })
                    
                    # Flag large files (>10MB)
                    if size > 10 * 1024 * 1024:
                        self.large_files.append({
                            'path': str(rel_path),
                            'size_mb': self.get_size_mb(size),
                            'extension': ext
                        })
                except (PermissionError, OSError):
                    pass
    
    def generate_report(self):
        report = []
        report.append("\n" + "="*80)
        report.append("PROJECT DIAGNOSTIC REPORT")
        report.append("="*80 + "\n")
        
        # Summary
        report.append(f"📁 Project Root: {self.root}")
        report.append(f"💾 Total Size: {self.get_size_mb(self.total_size):.2f} MB")
        report.append(f"📄 Total Files: {sum(len(files) for files in self.file_types.values())}")
        report.append(f"📑 File Types: {len(self.file_types)}\n")
        
        # Large Files Warning
        if self.large_files:
            report.append("\n⚠️  LARGE FILES DETECTED (>10MB)")
            report.append("-" * 80)
            self.large_files.sort(key=lambda x: x['size_mb'], reverse=True)
            for f in self.large_files:
                report.append(f"  {f['size_mb']:>8.2f} MB  | {f['path']}")
        
        # Suspicious Files by Type
        suspicious_found = defaultdict(list)
        for ext, files in self.file_types.items():
            if ext in self.suspicious_extensions:
                total_size = sum(f['size'] for f in files)
                suspicious_found[ext] = {
                    'count': len(files),
                    'total_size_mb': self.get_size_mb(total_size),
                    'files': files
                }
        
        if suspicious_found:
            report.append("\n\n🔍 POTENTIALLY PROBLEMATIC FILE TYPES")
            report.append("-" * 80)
            for ext, data in sorted(suspicious_found.items(), key=lambda x: x[1]['total_size_mb'], reverse=True):
                report.append(f"\n{ext.upper()} files: {data['count']} files, {data['total_size_mb']:.2f} MB total")
                if data['count'] <= 10:
                    for f in data['files']:
                        report.append(f"  - {f['path']} ({self.get_size_mb(f['size']):.2f} MB)")
                else:
                    for f in data['files'][:5]:
                        report.append(f"  - {f['path']} ({self.get_size_mb(f['size']):.2f} MB)")
                    report.append(f"  ... and {data['count'] - 5} more")
        
        # File Type Summary
        report.append("\n\n📊 FILE TYPE SUMMARY")
        report.append("-" * 80)
        type_summary = []
        for ext, files in self.file_types.items():
            total_size = sum(f['size'] for f in files)
            type_summary.append((ext or '[no extension]', len(files), self.get_size_mb(total_size)))
        
        type_summary.sort(key=lambda x: x[2], reverse=True)
        for ext, count, size_mb in type_summary[:20]:
            report.append(f"  {ext:.<20} {count:>4} files, {size_mb:>8.2f} MB")
        
        # Directory Structure
        report.append("\n\n🌳 DIRECTORY STRUCTURE")
        report.append("-" * 80)
        dirs = set()
        for files in self.file_types.values():
            for f in files:
                path = Path(f['path'])
                if len(path.parts) > 1:
                    dirs.add(path.parts[0])
        
        for d in sorted(dirs):
            dir_path = self.root / d
            if dir_path.is_dir():
                file_count = sum(1 for _ in dir_path.rglob('*') if _.is_file())
                report.append(f"  📂 {d}/ ({file_count} files)")
        
        return "\n".join(report)
    
    def generate_gitignore(self):
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Machine Learning Models
*.h5
*.pt
*.pth
*.ckpt
*.pb
*.onnx
*.tflite
*.pkl
*.joblib
*.model
*.weights
models/
checkpoints/
saved_models/

# Data Files
*.csv
*.parquet
*.hdf5
*.npy
*.npz
data/
datasets/
raw_data/

# Videos
*.mp4
*.avi
*.mov
*.mkv
*.flv
*.wmv
*.webm
videos/

# Large Media
*.mp3
*.wav
*.flac
*.ogg

# Images (consider what you need)
# *.jpg
# *.jpeg
# *.png
# *.gif

# Database
*.db
*.sqlite
*.sqlite3

# Archives
*.zip
*.tar
*.gz
*.rar
*.7z

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb

# Environment
.env
.env.local
*.env

# Logs
logs/
*.log

# OS
Thumbs.db
.DS_Store

# Node (if using JS)
node_modules/
package-lock.json

# Temporary files
tmp/
temp/
*.tmp
"""
        return gitignore_content
    
    def save_report(self, filename="project_diagnostic_report.txt"):
        report = self.generate_report()
        report_path = self.root / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ Report saved to: {report_path}")
        return report
    
    def save_gitignore(self):
        gitignore_path = self.root / '.gitignore'
        content = self.generate_gitignore()
        
        if gitignore_path.exists():
            print(f"\n⚠️  .gitignore already exists at {gitignore_path}")
            print("Creating .gitignore.recommended instead...")
            gitignore_path = self.root / '.gitignore.recommended'
        
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Gitignore saved to: {gitignore_path}")


def main():
    # Set your project path here
    project_path = r"D:\Users\Anoshia\BattingEdge_FYP"
    
    print("🔍 Starting Project Diagnostic...")
    print("This will scan your project and identify potential issues before GitHub commit.\n")
    
    diagnostic = ProjectDiagnostic(project_path)
    diagnostic.scan_directory()
    report = diagnostic.save_report()
    diagnostic.save_gitignore()
    
    print("\n" + "="*80)
    print(report)
    print("\n" + "="*80)
    print("\n✅ DIAGNOSTIC COMPLETE!")
    print("\nNext steps:")
    print("1. Review the report above")
    print("2. Check project_diagnostic_report.txt for full details")
    print("3. Update your .gitignore based on .gitignore.recommended")
    print("4. Remove or move large files/models/videos before committing")
    print("5. Share the report with me for review!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()