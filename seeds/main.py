import os
import subprocess
import sys

def main():
    print("APP_ENV =", os.getenv("APP_ENV"))
    print("SEED_COUNT =", os.getenv("SEED_COUNT"))

    max_ver = int(os.getenv("MIGRATION_VERSION", "999"))
    if os.getenv("APP_ENV") != "dev":
        print("APP_ENV != dev — skip seeding.")
        return

    sequence = [
        (1, "seed_v1__core_data.py"),
        (2, "seed_v2__interactions.py"),
        (3, "seed_v3__utilities.py"),
    ]

    for ver, script in sequence:
        if ver <= max_ver:
            ret = subprocess.run([sys.executable, f"/seeds/{script}"])
            if ret.returncode != 0:
                print(f"Error {script}", file=sys.stderr)
                sys.exit(ret.returncode)

if __name__ == "__main__":
    main()
