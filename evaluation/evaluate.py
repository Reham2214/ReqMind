from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# =========================================================
# PATHS
# =========================================================

DATASET_PATH = Path(
    "data/ReqMind Dataset.xlsx"
)

DEFAULT_PREDICTIONS_PATH = Path(
    "data/predictions.csv"
)


# =========================================================
# LABEL NORMALIZATION
# =========================================================

def normalize_label(label):

    if pd.isna(label):
        return ""

    label = str(label).strip()

    replacements = {
        "No issue": "No Issue",
        "No Issue": "No Issue",

        "Non Verifiable": "Non-verifiable",
        "Non-verifiable": "Non-verifiable",
        "non-verifiable": "Non-verifiable",

        "Ambiguous": "Ambiguity",
        "Ambiguity": "Ambiguity",

        "Incomplete": "Incompleteness",
        "Incompleteness": "Incompleteness",

        "Inconsistent": "Inconsistency",
        "Inconsistency": "Inconsistency",

        "Duplicate": "Duplication",
        "Duplication": "Duplication",

        "Conflict": "Conflict",
    }

    return replacements.get(
        label,
        label,
    )


# =========================================================
# EVALUATION
# =========================================================

def evaluate_predictions(
    predictions_path=DEFAULT_PREDICTIONS_PATH,
):

    try:

        predictions_path = Path(
            predictions_path
        )

        if not predictions_path.exists():

            return {
                "success": False,
                "error": (
                    f"Predictions file not found: "
                    f"{predictions_path}"
                ),
            }

        if not DATASET_PATH.exists():

            return {
                "success": False,
                "error": (
                    f"Dataset file not found: "
                    f"{DATASET_PATH}"
                ),
            }

        # -------------------------------------------------
        # Predictions
        # -------------------------------------------------

        predictions_df = pd.read_csv(
            predictions_path
        )

        if "ID" not in predictions_df.columns:

            return {
                "success": False,
                "error": (
                    "Predictions file is missing "
                    "the ID column."
                ),
            }

        if (
            "Issue_Label"
            not in predictions_df.columns
        ):

            return {
                "success": False,
                "error": (
                    "Predictions file is missing "
                    "the Issue_Label column."
                ),
            }

        predictions_df = predictions_df[
            [
                "ID",
                "Issue_Label",
            ]
        ].copy()

        # -------------------------------------------------
        # Ground Truth
        # -------------------------------------------------

        ground_truth_df = pd.read_excel(
            DATASET_PATH,
            sheet_name="Ground_Truth",
        )

        if "ID" not in ground_truth_df.columns:

            return {
                "success": False,
                "error": (
                    "Ground_Truth is missing "
                    "the ID column."
                ),
            }

        if (
            "Issue_Label"
            not in ground_truth_df.columns
        ):

            return {
                "success": False,
                "error": (
                    "Ground_Truth is missing "
                    "the Issue_Label column."
                ),
            }

        ground_truth_df = ground_truth_df[
            [
                "ID",
                "Issue_Label",
            ]
        ].copy()

        # -------------------------------------------------
        # Normalize IDs
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Normalize labels
        # -------------------------------------------------

        predictions_df[
            "Issue_Label"
        ] = predictions_df[
            "Issue_Label"
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

        # -------------------------------------------------
        # Merge by ID
        # -------------------------------------------------

        merged_df = pd.merge(
            ground_truth_df,
            predictions_df,
            on="ID",
            how="inner",
            suffixes=(
                "_true",
                "_pred",
            ),
        )

        if merged_df.empty:

            return {
                "success": False,
                "error": (
                    "No matching IDs were found "
                    "between predictions and Ground_Truth."
                ),
            }

        # -------------------------------------------------
        # Actual labels
        # -------------------------------------------------

        y_true = merged_df[
            "Issue_Label_true"
        ]

        y_pred = merged_df[
            "Issue_Label_pred"
        ]

        labels = sorted(
            set(y_true)
            | set(y_pred)
        )

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------

        precision = precision_score(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0,
        )

        recall = recall_score(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0,
        )

        # -------------------------------------------------
        # Classification report
        # -------------------------------------------------

        report = classification_report(
            y_true,
            y_pred,
            labels=labels,
            output_dict=True,
            zero_division=0,
        )

        # -------------------------------------------------
        # Confusion matrix
        # -------------------------------------------------

        matrix = confusion_matrix(
            y_true,
            y_pred,
            labels=labels,
        ).tolist()

        # -------------------------------------------------
        # Return
        # -------------------------------------------------

        return {
            "success": True,

            "precision": float(
                precision
            ),

            "recall": float(
                recall
            ),

            "f1": float(
                f1
            ),

            "matched_ids": int(
                len(merged_df)
            ),

            "ground_truth_count": int(
                len(ground_truth_df)
            ),

            "prediction_count": int(
                len(predictions_df)
            ),

            "classification_report": report,

            "confusion_matrix": matrix,

            "labels": labels,

            "ground_truth_file": str(
                DATASET_PATH
            ),

            "ground_truth_sheet": (
                "Ground_Truth"
            ),

            "ground_truth_label_column": (
                "Issue_Label"
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# COMPATIBILITY
# =========================================================

def evaluate(
    predictions_path=DEFAULT_PREDICTIONS_PATH,
):

    return evaluate_predictions(
        predictions_path
    )