"""
======================================================================
  WhatsApp Invitation Sender
======================================================================
  HOW TO USE
  1. Fill in guests.csv  (name, phone, display_name — one row per guest).
     phone must include the country code, e.g. +94771234567
  2. Run:  python send_invitations.py
     Chrome will open WhatsApp Web — scan the QR code on first run.
     Your login is saved, so you only scan once.
  3. Dry-run (generate images + preview messages, no sending):
     python send_invitations.py --dry-run

  INSTALL
  pip install selenium Pillow
======================================================================
"""

import argparse
import csv
import subprocess
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from make_invitations import personalize, safe_filename, FONT, BASE_IMAGE

# ---------------------------------------------------------------- MESSAGE
MESSAGE_TEMPLATE = """\
Dear {display_name},

custom message here

With all our love
"""

# ---------------------------------------------------------------- CONFIG
CHAT_LOAD_TIMEOUT = 60   # seconds to wait for WhatsApp Web chat to load
GAP_BETWEEN       = 5    # seconds between guests
CSV_FILE          = "guests.csv"
OUT_DIR           = Path("invitations")
PROFILE_DIR       = str(Path.home() / ".whatsapp_sender_profile")  # persists login

# ---------------------------------------------------------------- BROWSER
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    return webdriver.Chrome(options=options)

# ---------------------------------------------------------------- SEND
def _find(driver, timeout, *xpaths):
    """Try multiple XPaths in order, return the first element found."""
    for xpath in xpaths:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except Exception:
            continue
    raise Exception(f"None of these XPaths matched within {timeout}s:\n" + "\n".join(xpaths))

def _click(driver, timeout, *xpaths):
    """Try multiple XPaths in order, click the first clickable element found."""
    for xpath in xpaths:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            el.click()
            return el
        except Exception:
            continue
    raise Exception(f"None of these XPaths were clickable within {timeout}s:\n" + "\n".join(xpaths))

def send_image(driver, phone, img_path_abs, message):
    driver.get(f"https://web.whatsapp.com/send?phone={phone}")

    # Wait for compose box to confirm chat loaded
    _find(driver, CHAT_LOAD_TIMEOUT,
        '//div[@data-testid="conversation-compose-box-input"]',
        '//div[@contenteditable="true"][@data-tab="10"]',
    )
    time.sleep(2)

    # 1. Copy image to clipboard via osascript, then paste into compose box.
    #    This routes the image through Photos & Videos (not sticker mode).
    subprocess.run([
        'osascript', '-e',
        f'set the clipboard to (read (POSIX file "{img_path_abs}") as JPEG picture)',
    ], check=True)
    time.sleep(0.5)

    compose = _find(driver, 10,
        '//div[@data-testid="conversation-compose-box-input"]',
        '//div[@contenteditable="true"][@data-tab="10"]',
    )
    compose.click()
    ActionChains(driver).key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
    time.sleep(2)

    # 2. Type personalised message in the caption field via clipboard
    caption = _find(driver, 15,
        '//div[@data-testid="media-caption-input-container"]',
        '//div[@contenteditable="true"][@data-tab="undefined"]',
        '//div[@contenteditable="true"][not(@data-testid="conversation-compose-box-input")][@spellcheck="true"]',
    )
    driver.execute_script("arguments[0].click();", caption)
    time.sleep(0.3)
    subprocess.run(['pbcopy'], input=message.encode('utf-8'), check=True)
    ActionChains(driver).key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
    time.sleep(0.5)

    # 3. Send
    _click(driver, 10,
        '//*[@aria-label="Send 1 selected"][@role="button"]',
        '//*[starts-with(@aria-label,"Send")][@role="button"]',
        '//button[@aria-label="Send"]',
    )
    time.sleep(3)

# ---------------------------------------------------------------- MAIN
def main(dry_run=False):
    OUT_DIR.mkdir(exist_ok=True)

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        guests = [row for row in csv.DictReader(f) if row["name"].strip()]

    label = "DRY RUN" if dry_run else "Sending"
    print(f"{label} — {len(guests)} invitation(s)...\n")

    driver = None
    if not dry_run:
        print("Opening Chrome — scan the QR code if prompted, then wait...")
        driver = get_driver()
        driver.get("https://web.whatsapp.com")
        input("Press ENTER once WhatsApp Web is fully loaded and ready > ")

    try:
        for i, guest in enumerate(guests, 1):
            name         = guest["name"].strip()
            phone        = guest["phone"].strip().replace(" ", "")
            display_name = guest["display_name"].strip()

            # 1. Generate personalised invitation image
            img_path = OUT_DIR / f"A_A_{safe_filename(name)}.png"
            personalize(name, BASE_IMAGE, FONT, img_path)
            print(f"[{i}/{len(guests)}] Image saved → {img_path}")

            # 2. Build personalised message
            message = MESSAGE_TEMPLATE.format(display_name=display_name)

            if dry_run:
                print(f"         [dry-run] Would send to {phone} ({display_name})")
                print(f"         Message preview:\n")
                print("\n".join(f"           {l}" for l in message.splitlines()))
                print()
                continue

            # 3. Send
            print(f"         Sending to {phone} ({display_name})...")
            send_image(driver, phone, img_path.resolve(), message)
            print(f"         Sent!\n")

            if i < len(guests):
                time.sleep(GAP_BETWEEN)

    finally:
        if driver:
            driver.quit()

    print(f"Done — {len(guests)} invitation(s) {'previewed' if dry_run else 'sent'}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send wedding invitations via WhatsApp.")
    parser.add_argument("--dry-run", action="store_true", help="Generate images and preview messages without sending.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
