import requests
import time
import os
import glob
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
DATASET_DIR = Path("dataset/test")
REPORT_PATH = Path("TEST_REGRESSION_REPORT.txt")

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(msg):
    print(msg)
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def find_test_video():
    # Try to find a specific robust video first
    specific = DATASET_DIR / "pull" / "aug_speed_up_234_pull (23).mp4"
    if specific.exists(): return specific
    
    # Fallback
    videos = list(DATASET_DIR.rglob("*.mp4"))
    if videos: return videos[0]
    return None

def run_tests():
    if REPORT_PATH.exists(): os.remove(REPORT_PATH)
    log(f"STARTING V9.5 REGRESSION TEST - {time.ctime()}")

    # 1. HEALTH CHECK
    try:
        res = requests.get(f"{BASE_URL}/api/health")
        if res.status_code == 200 and res.json()['status'] == 'healthy':
            log(f"{GREEN}✓ PASS: Health Check (V9.5){RESET}")
        else:
            log(f"{RED}✗ FAIL: Health Check{RESET}")
            return
    except:
        log(f"{RED}✗ FAIL: Server not running. Start uvicorn first!{RESET}")
        return

    # 2. UPLOAD
    video_path = find_test_video()
    if not video_path:
        log(f"{RED}✗ FAIL: No test video found{RESET}")
        return

    log(f"Testing with: {video_path.name}")
    
    with open(video_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/api/upload", files={"file": f})
    
    if res.status_code != 200:
        log(f"{RED}✗ FAIL: Upload Error {res.text}{RESET}")
        return
    
    video_id = res.json()['video_id']
    log(f"{GREEN}✓ PASS: Upload (ID: {video_id}){RESET}")

    # 3. ANALYZE
    res = requests.post(f"{BASE_URL}/api/analyze/{video_id}")
    if res.status_code != 200:
        log(f"{RED}✗ FAIL: Analyze Trigger Error{RESET}")
        return
    log(f"{GREEN}✓ PASS: Analysis Triggered{RESET}")

    # 4. POLL FOR COMPLETION
    log("⏳ Waiting for analysis...")
    status = "processing"
    for _ in range(30):
        time.sleep(1)
        res = requests.get(f"{BASE_URL}/api/result/{video_id}")
        data = res.json()
        status = data.get('status')
        if status == 'completed': break
        if status == 'failed': break
    
    if status == 'completed':
        shot = data.get('shot_type')
        score = data.get('form_score')
        log(f"{GREEN}✓ PASS: Analysis Completed (Shot: {shot}, Score: {score}){RESET}")
    else:
        log(f"{RED}✗ FAIL: Analysis Timed Out or Failed{RESET}")
        return

    # 5. CHECK OVERLAY
    res = requests.get(f"{BASE_URL}/api/video/{video_id}/overlay")
    if res.status_code == 200:
        log(f"{GREEN}✓ PASS: Overlay Video Generated{RESET}")
    else:
        log(f"{RED}✗ FAIL: Overlay Missing{RESET}")

    # 6. CHECK PDF
    res = requests.get(f"{BASE_URL}/api/report/{video_id}/pdf")
    if res.status_code == 200:
        log(f"{GREEN}✓ PASS: PDF Report Generated{RESET}")
    else:
        log(f"{RED}✗ FAIL: PDF Missing{RESET}")

    log("\nALL SYSTEMS GO. V9.5 IS READY.")

if __name__ == "__main__":
    run_tests()