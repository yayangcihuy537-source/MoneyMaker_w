import time
import sys
import json
import warnings
import os

warnings.filterwarnings('ignore')
os.environ["PYTHONWARNINGS"] = "ignore"

def log(msg):
    print(msg, file=sys.stderr)

try:
    from seledroid import webdriver
    from seledroid.webdriver.common.by import By
except ImportError:
    log("install Seledroid module and Apk")
    sys.exit(1)

def usage():
    log("Usage:")
    log("  python tes.py <url>")
    sys.exit(1)

def interstitial(url):
    driver = webdriver.Chrome(gui=True, pip_mode=True)
    driver.get(url)
    log(f"capturing interstitial: {url}")

    clearance = None
    MAX_WAIT = 20
    INTERVAL = 2
    elapsed = 0

    while elapsed < MAX_WAIT:
        clearance = driver.get_cookie("cf_clearance")
        if clearance:
            log("cf_clearance obtained")
            break
        time.sleep(INTERVAL)
        elapsed += INTERVAL

    try:
        uagent = driver.user_agent
    except Exception:
        try:
            uagent = driver.execute_script("return navigator.userAgent;")
        except Exception:
            uagent = None

    driver.close()
    return {
        "cf_clearance": clearance,
        "user_agent": uagent
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    TARGET_URL = sys.argv[1]
    
    result = interstitial(TARGET_URL)
    print(json.dumps(result))
