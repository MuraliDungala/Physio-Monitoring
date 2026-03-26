import argparse
import csv
import os
import re
from pathlib import Path

import pandas as pd

# Mapping: external folder IDs -> internal exercise names
KIMORE_EXERCISE_MAP = {
    "ex1": "Shoulder Flexion",
    "ex2": "Shoulder Abduction",
    "ex3": "Shoulder External Rotation",
    "ex4": "Shoulder Internal Rotation",
    "ex5": "Knee Flexion",
}

UI_PMRD_EXERCISE_MAP = {
    "ex1": "Shoulder Abduction",
    "ex2": "Shoulder Adduction",
    "ex3": "Shoulder Flexion",
    "ex4": "Shoulder Extension",
    "ex5": "Shoulder Internal Rotation",
    "ex6": "Shoulder External Rotation",
    "ex7": "Elbow Flexion",
    "ex8": "Elbow Extension",
    "ex9": "Wrist Flexion",
    "ex10": "Wrist Extension",
}


def _extract_ex_id(name: str) -> str | None:
    match = re.search(r"ex(\d+)", name, re.IGNORECASE)
    if not match:
        return None
    return f"ex{match.group(1)}"


def _normalize_row(row, target_features: int) -> list[float]:
    values = [float(v) for v in row]
    if len(values) < target_features:
        values.extend([0.0] * (target_features - len(values)))
    elif len(values) > target_features:
        values = values[:target_features]
    return values


def _write_header(writer, target_features: int) -> None:
    header = [f"joint_{i}" for i in range(target_features)] + ["exercise_label"]
    writer.writerow(header)


def _process_kimore(root: Path, writer, target_features: int) -> int:
    count = 0
    for train_x in root.glob("**/Train_X.csv"):
        ex_id = _extract_ex_id(train_x.parent.name)
        if not ex_id:
            continue
        label = KIMORE_EXERCISE_MAP.get(ex_id)
        if not label:
            print(f"[WARN] KIMORE: No label mapping for {train_x.parent.name}. Skipping.")
            continue

        df = pd.read_csv(train_x, header=None)
        for row in df.itertuples(index=False, name=None):
            features = _normalize_row(row, target_features)
            writer.writerow(features + [label])
            count += 1

    return count


def _process_ui_pmrd(root: Path, writer, target_features: int) -> int:
    count = 0
    for ex_dir in root.glob("UI_PRMD_ex*"):
        if not ex_dir.is_dir():
            continue
        ex_id = _extract_ex_id(ex_dir.name)
        if not ex_id:
            continue
        label = UI_PMRD_EXERCISE_MAP.get(ex_id)
        if not label:
            print(f"[WARN] UI-PMRD: No label mapping for {ex_dir.name}. Skipping.")
            continue

        data_files = sorted(ex_dir.glob("Data_*.csv"))
        if not data_files:
            print(f"[WARN] UI-PMRD: No data files in {ex_dir.name}. Skipping.")
            continue

        for data_file in data_files:
            df = pd.read_csv(data_file, header=None)
            for row in df.itertuples(index=False, name=None):
                features = _normalize_row(row, target_features)
                writer.writerow(features + [label])
                count += 1

    return count


def preprocess_datasets(kimore_root: Path, ui_pmrd_root: Path, output_file: Path,
                        target_features: int) -> None:
    os.makedirs(output_file.parent, exist_ok=True)

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        _write_header(writer, target_features)

        kimore_count = _process_kimore(kimore_root, writer, target_features)
        ui_pmrd_count = _process_ui_pmrd(ui_pmrd_root, writer, target_features)

    print("[DONE] Preprocessing complete")
    print(f"  Output: {output_file}")
    print(f"  KIMORE samples: {kimore_count}")
    print(f"  UI-PMRD samples: {ui_pmrd_count}")
    print(f"  Total samples: {kimore_count + ui_pmrd_count}")
    print(f"  Features per sample: {target_features}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess KIMORE and UI-PMRD datasets into a single CSV"
    )
    parser.add_argument(
        "--kimore-root",
        default="data/external/KIMORE",
        help="Path to KIMORE dataset root",
    )
    parser.add_argument(
        "--ui-pmrd-root",
        default="data/external/UI-PMRD",
        help="Path to UI-PMRD dataset root",
    )
    parser.add_argument(
        "--output",
        default="data/processed_keypoints/external_exercises.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--target-features",
        type=int,
        default=132,
        help="Number of features per row (pads or truncates)",
    )

    args = parser.parse_args()

    preprocess_datasets(
        Path(args.kimore_root),
        Path(args.ui_pmrd_root),
        Path(args.output),
        args.target_features,
    )


if __name__ == "__main__":
    main()
