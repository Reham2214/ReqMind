import os
import sys
from pathlib import Path

import pandas as pd

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================================
# Imports
# ==========================================================

from graph import analyze_requirements_direct
from utils.schemas import Requirement
from evaluation.evaluate import evaluate_predictions


# ==========================================================
# Paths
# ==========================================================

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "ReqMind Dataset.xlsx"
)

PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "predictions.csv"
)


# ==========================================================
# Load Dataset
# ==========================================================

def load_requirements():
    print("Loading dataset...")

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_excel(
        DATASET_PATH,
        sheet_name="Requirement",
    )

    required_columns = [
        "ID",
        "Requirement",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    requirements = []

    for _, row in df.iterrows():

        requirement_id = str(
            row["ID"]
        ).strip()

        requirement_text = str(
            row["Requirement"]
        ).strip()

        if not requirement_id:
            continue

        if not requirement_text:
            continue

        requirements.append(
            Requirement(
                id=requirement_id,
                text=requirement_text,
            )
        )

    print(
        f"Loaded {len(requirements)} requirements."
    )

    return requirements


# ==========================================================
# Save Predictions
# ==========================================================

def save_predictions(results):

    prediction_rows = []

    for result in results:

        prediction_rows.append(
            {
                "ID": result.requirement_id,
                "Requirement": result.requirement,
                "Predicted_Issue_Label": (
                    result.issue_label
                ),
                "Predicted_Severity": (
                    result.severity
                ),
                "Explanation": (
                    result.explanation
                ),
                "Evidence": (
                    result.evidence
                ),
                "Recommendation": (
                    result.recommendation
                ),
                "Improved_Requirement": (
                    result.improved_requirement
                ),
            }
        )

    predictions_df = pd.DataFrame(
        prediction_rows
    )

    predictions_df.to_csv(
        PREDICTIONS_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"\nPredictions saved to:"
        f"\n{PREDICTIONS_PATH}"
    )


# ==========================================================
# Main Evaluation
# ==========================================================

def main():

    print("=" * 60)
    print("ReqMind Developer Evaluation")
    print("=" * 60)

    # ------------------------------------------------------
    # Load Dataset
    # ------------------------------------------------------

    requirements = load_requirements()

    if not requirements:
        print(
            "No requirements found in dataset."
        )
        return

    # ------------------------------------------------------
    # Run ReqMind
    # ------------------------------------------------------

    print(
        "\nRunning ReqMind analysis..."
    )

    results = analyze_requirements_direct(
        requirements
    )

    print(
        f"\nAnalysis completed for "
        f"{len(results)} requirements."
    )

    # ------------------------------------------------------
    # Save Predictions
    # ------------------------------------------------------

    save_predictions(
        results
    )

    # ------------------------------------------------------
    # Evaluate Predictions
    # ------------------------------------------------------

    print("\nEvaluating predictions...")

    metrics = evaluate_predictions(
        PREDICTIONS_PATH
    )

    # ------------------------------------------------------
    # Display Results
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("Evaluation Results")
    print("=" * 60)

    print(
        f"Precision: {metrics['precision']:.4f}"
    )

    print(
        f"Recall:    {metrics['recall']:.4f}"
    )

    print(
        f"F1 Score:  {metrics['f1']:.4f}"
    )

    if "matched_ids" in metrics:
        print(
            f"\nMatched IDs: "
            f"{metrics['matched_ids']}"
        )

    if "ground_truth_count" in metrics:
        print(
            f"Ground Truth Count: "
            f"{metrics['ground_truth_count']}"
        )

    if "classification_report" in metrics:

        print(
            "\nClassification Report:"
        )

        print(
            metrics[
                "classification_report"
            ]
        )

    print("\nEvaluation completed.")


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":
    main()