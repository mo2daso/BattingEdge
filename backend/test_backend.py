import requests
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
# Adjust this path if you want to test a specific video
TEST_VIDEO_PATH = Path("data/dataset_v7_clean/test/drive/drive_test_001.mp4") 
REPORT_PATH = Path("backend/test_report.txt")

# Colors for terminal
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(message, status="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [{status}] {message}"
    
    # Print to console (safe)
    try:
        print(formatted_msg)
    except UnicodeEncodeError:
        # Fallback for terminals that don't support emojis
        print(formatted_msg.encode('ascii', 'ignore').decode('ascii'))

    # Write to file (FIXED: Added encoding='utf-8')
    with open(REPORT_PATH, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

def run_tests():
    # Clear previous report
    if REPORT_PATH.exists():
        os.remove(REPORT_PATH)
    
    log("STARTING BACKEND AUTOMATED TESTS", "INIT")
    
    video_id = None

    # --- TEST 1: HEALTH CHECK ---
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/health")
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'healthy' and data['model_loaded']:
                print(f"{GREEN}✓ PASS: Health Check ({duration:.2f}s){RESET}")
                log("Health Check Passed", "PASS")
            else:
                print(f"{RED}✗ FAIL: Health Check - Invalid Response{RESET}")
                log(f"Health Check Failed: {data}", "FAIL")
        else:
            print(f"{RED}✗ FAIL: Health Check - Status {response.status_code}{RESET}")
            log(f"Health Check Failed: {response.status_code}", "FAIL")
    except Exception as e:
        print(f"{RED}✗ FAIL: Health Check - Connection Error{RESET}")
        log(f"Health Check Error: {e}", "ERROR")
        return # Stop if server is down

    # --- TEST 2: UPLOAD VIDEO ---
    # Ensure test video exists, otherwise pick the first available one
    if not TEST_VIDEO_PATH.exists():
        # Fallback search
        found = list(Path("data").rglob("*.mp4"))
        if found:
            TEST_VIDEO_PATH_ACTUAL = found[0]
        else:
            log("No videos found for testing", "ERROR")
            print(f"{RED}✗ SKIPPING: Test video missing{RESET}")
            return
    else:
        TEST_VIDEO_PATH_ACTUAL = TEST_VIDEO_PATH

    try:
        start = time.time()
        with open(TEST_VIDEO_PATH_ACTUAL, "rb") as f:
            files = {"file": ("test_video.mp4", f, "video/mp4")}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        duration = time.time() - start

        if response.status_code == 200:
            video_id = response.json().get("video_id")
            print(f"{GREEN}✓ PASS: Upload Video ({duration:.2f}s) -> ID: {video_id}{RESET}")
            log(f"Upload Passed. ID: {video_id}", "PASS")
        else:
            print(f"{RED}✗ FAIL: Upload Video{RESET}")
            log(f"Upload Failed: {response.text}", "FAIL")
            return
    except Exception as e:
        log(f"Upload Error: {e}", "ERROR")
        return

    # --- TEST 3: INVALID FILE UPLOAD ---
    try:
        # Create dummy text file
        with open("dummy.txt", "w") as f: f.write("test")
        
        with open("dummy.txt", "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 400:
            print(f"{GREEN}✓ PASS: Invalid File Rejection{RESET}")
            log("Invalid File Test Passed", "PASS")
        else:
            print(f"{RED}✗ FAIL: Invalid File Accepted (Status {response.status_code}){RESET}")
            log("Invalid File Test Failed", "FAIL")
        
        os.remove("dummy.txt")
    except Exception as e:
        log(f"Invalid Upload Error: {e}", "ERROR")

    # --- TEST 4: ANALYZE VIDEO ---
    try:
        start = time.time()
        response = requests.post(f"{BASE_URL}/api/analyze/{video_id}")
        
        if response.status_code == 200:
            print(f"{GREEN}✓ PASS: Analysis Triggered{RESET}")
            log("Analysis Triggered", "PASS")
        else:
            print(f"{RED}✗ FAIL: Analysis Trigger{RESET}")
            log(f"Analysis Failed: {response.text}", "FAIL")
            return
    except Exception as e:
        log(f"Analysis Error: {e}", "ERROR")
        return

    # --- TEST 5: POLLING RESULTS ---
    print("⏳ Waiting for analysis to complete...")
    for _ in range(30): # Wait up to 30 seconds
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/api/result/{video_id}")
        data = response.json()
        
        if data.get("status") == "completed":
            print(f"{GREEN}✓ PASS: Analysis Completed{RESET}")
            print(f"   -> Shot: {data.get('shot_type')}")
            print(f"   -> Form Score: {data.get('form_score')}")
            log("Analysis Completed Successfully", "PASS")
            break
        elif data.get("status") == "failed":
            print(f"{RED}✗ FAIL: Analysis Error Reported by Server{RESET}")
            log(f"Server reported failure: {data.get('error_message')}", "FAIL")
            break
    else:
        print(f"{RED}✗ FAIL: Analysis Timed Out{RESET}")
        log("Analysis Timeout", "FAIL")

    # --- TEST 6: DOWNLOAD OVERLAY ---
    try:
        response = requests.get(f"{BASE_URL}/api/video/{video_id}/overlay")
        if response.status_code == 200:
            size_mb = len(response.content) / (1024*1024)
            print(f"{GREEN}✓ PASS: Download Overlay ({size_mb:.2f} MB){RESET}")
            log("Download Overlay Passed", "PASS")
        else:
            print(f"{RED}✗ FAIL: Download Overlay{RESET}")
            log("Download Overlay Failed", "FAIL")
    except Exception as e:
        log(f"Download Error: {e}", "ERROR")

    # --- TEST 7: DELETE VIDEO ---
    try:
        response = requests.delete(f"{BASE_URL}/api/video/{video_id}")
        if response.status_code == 200:
            print(f"{GREEN}✓ PASS: Delete Record{RESET}")
            log("Delete Record Passed", "PASS")
        else:
            print(f"{RED}✗ FAIL: Delete Record{RESET}")
            log("Delete Record Failed", "FAIL")
    except Exception as e:
        log(f"Delete Error: {e}", "ERROR")

    print(f"\n📄 Report saved to: {REPORT_PATH}")

if __name__ == "__main__":
    run_tests()