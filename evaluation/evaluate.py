import os

import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


GROUND_TRUTH_PATH = "data/ground_truth.xlsx"


def evaluate():

    # Check if the Ground Truth file exists
    if not os.path.exists(GROUND_TRUTH_PATH):

        return {
            "error": (
                "Ground Truth file not found. "
                "Automatic evaluation cannot be calculated yet."
            ),
            "precision": None,
            "recall": None,
            "f1": None,
            "requirements_evaluated": 0,
            "report": None,
            "confusion_matrix": None,
        }

    try:

        # Read Ground Truth sheet
        ground_truth = pd.read_excel(
            GROUND_TRUTH_PATH,
            sheet_name="Ground_Truth",
        )

    except ValueError:

        return {
            "error": (
                "The Excel file does not contain a sheet "
                "named 'Ground_Truth'. "
                "Please create a sheet with this exact name."
            ),
            "precision": None,
            "recall": None,
            "f1": None,
            "requirements_evaluated": 0,
            "report": None,
            "confusion_matrix": None,
        }

    except Exception as e:

        return {
            "error": f"Could not read Ground Truth file: {e}",
            "precision": None,
            "recall": None,
            "f1": None,
            "requirements_evaluated": 0,
            "report": None,
            "confusion_matrix": None,
        }

    # Check required columns
    required_columns = [
        "ID",
        "Issue_Label",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in ground_truth.columns
    ]

    if missing_columns:

        return {
            "error": (
                "Ground Truth is missing required columns: "
                + ", ".join(missing_columns)
            ),
            "precision": None,
            "recall": None,
            "f1": None,
            "requirements_evaluated": 0,
            "report": None,
            "confusion_matrix": None,
        }

    # Check predictions file
    predictions_path = "data/predictions.csv"

    if not os.path.exists(predictions_path):

        return {
            "error": (
                "Predictions file not found. "
                "Run the requirements analysis first."
            ),
            "precision": None,
            "recall": None,
            "f1": None,
            "requirements_evaluated": 0,
            "report": None,
            "confusion_matrix": None,
        }

    predictions = pd.read_csv(
        predictions_path
    )

    # Check prediction columns
    if "ID" not in predictions.columns:
        return {
            "error": "Predictions file is missing the 'ID' column."
        }

    if "Issue_Label" not in predictions.columns:
        return {
            "error": (
                "Predictions file is missing "
                "'Issue_Label'."
            )
        }

    # Match Ground Truth and predictions
    merged = pd.merge(
        ground_truth[
            ["ID", "Issue_Label"]
        ],
        predictions[
            ["ID", "Issue_Label"]
        ],
        on="ID",
        suffixes=(
            "_true",
            "_pred",
        ),
    )

    if merged.empty:

        return {
            "error": (
                "No matching requirement IDs were found "
                "between Ground Truth and predictions."
            ),
            "precision": None,
            "recall": None,
            "f1": None,
            "requirements_evaluated": 0,
            "report": None,
            "confusion_matrix": None,
        }

    y_true = merged["Issue_Label_true"]

    y_pred = merged["Issue_Label_pred"]

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

    report = pd.DataFrame(
        classification_report(
            y_true,
            y_pred,
            output_dict=True,
            zero_division=0,
        )
    ).transpose()

    labels = sorted(
        set(y_true) | set(y_pred)
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    confusion_df = pd.DataFrame(
        matrix,
        index=labels,
        columns=labels,
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "requirements_evaluated": len(
            merged
        ),
        "report": report,
        "confusion_matrix": confusion_df,
        "error": None,
    }