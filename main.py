import RPi.GPIO as GPIO
import os
import time
import random

# === CONFIG ===
SENSOR_PIN = 17
MOISTURE_CHECK_INTERVAL = 1         # Fast check when dry
VOICE_LINE_COOLDOWN = 20            # Seconds between lines
MAX_DRY_LINES = 5
AUDIO_PLAYER = "mpg123"
BASE_PATH = "./lines"
DRY_LINES = os.path.join(BASE_PATH, "dry")
HAPPY_LINES = os.path.join(BASE_PATH, "happy")

# === SETUP ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

def play_random(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".mp3")]
    if files:
        file = random.choice(files)
        path = os.path.join(folder, file)
        print(f"🔊 Playing: {file}")
        os.system(f"{AUDIO_PLAYER} '{path}'")
    else:
        print(f"No files in {folder}")

def is_dry():
    # Flip logic: LOW = dry
    return GPIO.input(SENSOR_PIN) == 0

try:
    last_state = None
    last_voice_time = 0
    dry_line_count = 0

    while True:
        current_time = time.time()
        dry = is_dry()

        if dry != last_state:
            # State change (wet <-> dry)
            last_state = dry
            dry_line_count = 0  # reset counter on state change
            if not dry:
                print("[HAPPY]")
                play_random(HAPPY_LINES)
                last_voice_time = current_time
            else:
                print("[DRY]")

        if dry:
            if (current_time - last_voice_time >= VOICE_LINE_COOLDOWN) and (dry_line_count < MAX_DRY_LINES):
                play_random(DRY_LINES)
                last_voice_time = current_time
                dry_line_count += 1
            time.sleep(MOISTURE_CHECK_INTERVAL)
        else:
            # When happy, we don’t need to check as often
            time.sleep(5)

except KeyboardInterrupt:
    print("Shutting down.")
finally:
    GPIO.cleanup()
