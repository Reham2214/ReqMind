from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)


# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "predictions.csv"
)

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "ReqMind Dataset.xlsx"
)


# ==========================================================
# Label Normalization
# ==========================================================

def normalize_label(label):

    if pd.isna(label):
        return ""

    return str(label).strip()


# ==========================================================
# Evaluate Predictions
# ==========================================================

def evaluate_predictions(
    predictions_path=DEFAULT_PREDICTIONS_PATH
):

    predictions_path = Path(
        predictions_path
    )

    if not predictions_path.exists():
        raise FileNotFoundError(
            f"Predictions file not found: "
            f"{predictions_path}"
        )

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: "
            f"{DATASET_PATH}"
        )

    # ------------------------------------------------------
    # Load Predictions
    # ------------------------------------------------------

    predictions_df = pd.read_csv(
        predictions_path
    )

    # ------------------------------------------------------
    # Validate Prediction Columns
    # ------------------------------------------------------

    required_prediction_columns = [
        "ID",
        "Predicted_Issue_Label",
    ]

    missing_prediction_columns = [
        column
        for column in required_prediction_columns
        if column not in predictions_df.columns
    ]

    if missing_prediction_columns:
        raise ValueError(
            "Predictions file is missing required columns: "
            + ", ".join(
                missing_prediction_columns
            )
        )

    # ------------------------------------------------------
    # Load Ground Truth
    # ------------------------------------------------------

    ground_truth_df = pd.read_excel(
        DATASET_PATH,
        sheet_name="Ground_Truth",
    )

    # ------------------------------------------------------
    # Validate Ground Truth Columns
    # ------------------------------------------------------

    required_ground_truth_columns = [
        "ID",
        "Issue_Label",
    ]

    missing_ground_truth_columns = [
        column
        for column in required_ground_truth_columns
        if column not in ground_truth_df.columns
    ]

    if missing_ground_truth_columns:
        raise ValueError(
            "Ground_Truth sheet is missing required columns: "
            + ", ".join(
                missing_ground_truth_columns
            )
        )

    # ------------------------------------------------------
    # Normalize IDs
    # ------------------------------------------------------

    predictions_df["ID"] = (
        predictions_df["ID"]
        .astype(str)
        .str.strip()
    )

    ground_truth_df["ID"] = (
        ground_truth_df["ID"]
        .astype(str)
        .str.strip()
    )

    # ------------------------------------------------------
    # Normalize Labels
    # ------------------------------------------------------

    predictions_df[
        "Predicted_Issue_Label"
    ] = predictions_df[
        "Predicted_Issue_Label"
    ].apply(
        normalize_label
    )

    ground_truth_df[
        "Issue_Label"
    ] = ground_truth_df[
        "Issue_Label"
    ].apply(
        normalize_label
    )

    # ------------------------------------------------------
    # Merge Predictions with Ground Truth
    # ------------------------------------------------------

    merged_df = pd.merge(
        ground_truth_df[
            [
                "ID",
                "Issue_Label",
            ]
        ],
        predictions_df[
            [
                "ID",
                "Predicted_Issue_Label",
            ]
        ],
        on="ID",
        how="inner",
    )

    if merged_df.empty:
        raise ValueError(
            "No matching IDs were found between "
            "Ground_Truth and predictions."
        )

    # ------------------------------------------------------
    # True Labels
    # ------------------------------------------------------

    y_true = merged_df[
        "Issue_Label"
    ]

    # ------------------------------------------------------
    # Predicted Labels
    # ------------------------------------------------------

    y_pred = merged_df[
        "Predicted_Issue_Label"
    ]

    # ------------------------------------------------------
    # Classification Metrics
    # ------------------------------------------------------

    precision = precision_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    # ------------------------------------------------------
    # Classification Report
    # ------------------------------------------------------

    report = classification_report(
        y_true,
        y_pred,
        zero_division=0,
    )

    # ------------------------------------------------------
    # Return Metrics
    # ------------------------------------------------------

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matched_ids": len(merged_df),
        "ground_truth_count": len(
            ground_truth_df
        ),
        "classification_report": report,
    }


# ==========================================================
# Compatibility Wrapper
# ==========================================================

def evaluate(
    predictions_path=DEFAULT_PREDICTIONS_PATH
):

    return evaluate_predictions(
        predictions_path
    )


# ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    metrics = evaluate_predictions()

    print("=" * 60)
    print("ReqMind Evaluation")
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

    print(
        f"Matched IDs: "
        f"{metrics['matched_ids']}"
    )

    print(
        f"Ground Truth Count: "
        f"{metrics['ground_truth_count']}"
    )

    print(
        "\nClassification Report:"
    )

    print(
        metrics["classification_report"]
    )