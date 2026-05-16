import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

RUN_EVERY = 30
CYCLES = 5

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports.py"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = OUT_DIR / "audit.log"


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}\n"
    if LOG_PATH.exists():
        LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        LOG_PATH.write_text(line, encoding="utf-8")


def version_outputs():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Cautam toate fisierele generate in outputs care nu au deja timestamp
    for file in OUT_DIR.glob("*.*"):
        if file.name == "audit.log": continue
        if "_" not in file.stem or len(file.stem.split("_")[-1]) != 15:
            new_name = OUT_DIR / f"{file.stem}_{ts}{file.suffix}"
            file.rename(new_name)


def main():
    print("AUTO REPORT START")
    print("reports.py:", REPORTS)
    print("outputs", OUT_DIR)

    for i in range(1, CYCLES + 1):
        log(f"Cycle {i} started")

        res = subprocess.run(
            [sys.executable, str(REPORTS)],
            cwd=str(ROOT),
            capture_output=True,
            text=True
        )

        print(f"\n=== Cycle {i} ===\n")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print(res.stderr)

        if res.returncode == 0:
            # Prevenim suprascrierea
            version_outputs()
            log(f"Cycle {i} finished OK")
        else:
            log(f"Cycle {i} FAILED (code={res.returncode})")
            break

        if i < CYCLES:
            time.sleep(RUN_EVERY)

    print("AUTO REPORT END")


if __name__ == "__main__":
    main()