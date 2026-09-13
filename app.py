import streamlit as st
import pandas as pd

from graph import graph
from utils.file_parser import extract_text
from evaluation.evaluate import evaluate


st.set_page_config(
    page_title="ReqMind",
    page_icon="📋",
    layout="wide",
)


# =========================================================
# HEADER
# =========================================================

st.title("ReqMind")

st.subheader(
    "AI-Powered Software Requirements Analysis"
)

st.write(
    """
Upload a software requirements document and ReqMind
will analyze the requirements for ambiguity,
incompleteness, inconsistency, duplication,
conflicts, and non-verifiable requirements.
"""
)


# =========================================================
# EVALUATION METHODOLOGY
# =========================================================

with st.expander(
    "System Evaluation",
    expanded=True,
):

    st.markdown(
        """
### System will be evaluated using:

- **Precision**
- **Recall**
- **F1 Score**
- **Human evaluation of explanations and recommendations**

**Precision, Recall, and F1 Score** will be calculated
by comparing ReqMind predictions against a labeled
Ground Truth dataset.

**Human evaluation** will assess the quality,
correctness, clarity, and usefulness of the generated
explanations and recommendations.
"""
    )


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload Requirements Document",
    type=[
        "pdf",
        "docx",
        "txt",
    ],
)


if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    analyze_button = st.button(
        "Analyze Requirements",
        type="primary",
        use_container_width=True,
    )

    if analyze_button:

        try:

            # =================================================
            # STEP 1 — READ DOCUMENT
            # =================================================

            with st.status(
                "Reading requirements document...",
                expanded=True,
            ) as document_status:

                document_status.write(
                    "Extracting text from the uploaded file..."
                )

                file_bytes = (
                    uploaded_file.getvalue()
                )

                document_text = extract_text(
                    uploaded_file.name,
                    file_bytes,
                )

                if not document_text.strip():

                    document_status.update(
                        label="Document could not be read.",
                        state="error",
                    )

                    st.error(
                        "The uploaded document does not contain readable text."
                    )

                    st.stop()

                document_status.write(
                    "Document text extracted successfully."
                )

                document_status.update(
                    label="Document loaded successfully.",
                    state="complete",
                    expanded=False,
                )


            # =================================================
            # STEP 2 — RUN REQMIND
            # =================================================

            with st.status(
                "ReqMind is analyzing the requirements...",
                expanded=True,
            ) as analysis_status:

                analysis_status.write(
                    "Running requirement extraction..."
                )

                result = graph.invoke(
                    {
                        "document_text": document_text
                    }
                )

                final_results = result[
                    "final_results"
                ]

                analysis_status.write(
                    f"Analyzed {len(final_results)} requirements."
                )

                analysis_status.update(
                    label="Requirement analysis completed.",
                    state="complete",
                    expanded=False,
                )


            # =================================================
            # STEP 3 — CREATE PREDICTIONS
            # =================================================

            predictions = []

            for item in final_results:

                predictions.append(
                    {
                        "ID": item.requirement_id,
                        "Issue_Label": item.issue_label,
                        "Severity": item.severity,
                    }
                )


            predictions_df = pd.DataFrame(
                predictions
            )


            # =================================================
            # SAVE PREDICTIONS
            # =================================================

            predictions_df.to_csv(
                "data/predictions.csv",
                index=False,
                encoding="utf-8-sig",
            )


            # =================================================
            # SUCCESS
            # =================================================

            st.success(
                f"Analysis completed. "
                f"{len(final_results)} requirements analyzed."
            )


            # =================================================
            # RESULTS SUMMARY
            # =================================================

            st.divider()

            st.header(
                "Analysis Summary"
            )


            total_requirements = len(
                final_results
            )

            issue_count = sum(
                1
                for item in final_results
                if item.issue_label != "No Issue"
            )

            no_issue_count = sum(
                1
                for item in final_results
                if item.issue_label == "No Issue"
            )


            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Requirements",
                    total_requirements,
                )

            with col2:

                st.metric(
                    "Issues Detected",
                    issue_count,
                )

            with col3:

                st.metric(
                    "No Issue",
                    no_issue_count,
                )


            # =================================================
            # REQUIREMENT RESULTS
            # =================================================

            st.divider()

            st.header(
                "Requirements Analysis"
            )


            for item in final_results:

                with st.container():

                    st.subheader(
                        item.requirement_id
                    )

                    st.markdown(
                        f"""
**Requirement**

{item.requirement}
"""
                    )


                    col1, col2 = st.columns(2)


                    with col1:

                        st.markdown(
                            f"""
**Issue**

{item.issue_label}
"""
                        )


                    with col2:

                        st.markdown(
                            f"""
**Severity**

{item.severity}
"""
                        )


                    st.markdown(
                        f"""
**Explanation**

{item.explanation}
"""
                    )


                    st.markdown(
                        f"""
**Evidence**

{item.evidence}
"""
                    )


                    st.markdown(
                        f"""
**Recommendation**

{item.recommendation}
"""
                    )


                    st.markdown(
                        f"""
**Improved Requirement**

{item.improved_requirement}
"""
                    )


                    if item.sources:

                        with st.expander(
                            "Knowledge Sources"
                        ):

                            for source in item.sources:

                                st.write(
                                    f"- {source}"
                                )


                    st.divider()


            # =================================================
            # EVALUATION
            # =================================================

            st.header(
                "ReqMind Evaluation"
            )


            st.markdown(
                """
### System will be evaluated using:

1. **Precision**
2. **Recall**
3. **F1 Score**
4. **Human evaluation of explanations and recommendations**
"""
            )


            with st.spinner(
                "Calculating evaluation metrics..."
            ):

                evaluation = evaluate()


            # =================================================
            # EVALUATION ERROR / MISSING GROUND TRUTH
            # =================================================

            if evaluation.get("error"):

                st.warning(
                    evaluation["error"]
                )

                st.info(
                    """
Automatic Precision, Recall, and F1 Score
will be available once the Ground Truth dataset
is prepared.

The current ReqMind analysis results are still
available above.
"""
                )


            else:

                st.success(
                    "Automatic evaluation completed."
                )


                # ---------------------------------------------
                # METRICS
                # ---------------------------------------------

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Precision",
                        f"{evaluation['precision']:.2%}",
                    )


                with col2:

                    st.metric(
                        "Recall",
                        f"{evaluation['recall']:.2%}",
                    )


                with col3:

                    st.metric(
                        "F1 Score",
                        f"{evaluation['f1']:.2%}",
                    )


                st.write(
                    f"Requirements evaluated: "
                    f"{evaluation['requirements_evaluated']}"
                )


                # ---------------------------------------------
                # CLASSIFICATION REPORT
                # ---------------------------------------------

                st.subheader(
                    "Classification Report"
                )

                st.dataframe(
                    evaluation["report"],
                    use_container_width=True,
                )


                # ---------------------------------------------
                # CONFUSION MATRIX
                # ---------------------------------------------

                st.subheader(
                    "Confusion Matrix"
                )

                st.dataframe(
                    evaluation["confusion_matrix"],
                    use_container_width=True,
                )


            # =================================================
            # HUMAN EVALUATION
            # =================================================

            st.divider()

            st.subheader(
                "Human Evaluation"
            )

            st.write(
                """
The explanations and recommendations generated
by ReqMind will be evaluated by human reviewers
based on criteria such as correctness, clarity,
relevance, and usefulness.
"""
            )


            # =================================================
            # DOWNLOAD
            # =================================================

            st.divider()

            csv_data = (
                predictions_df
                .to_csv(index=False)
                .encode("utf-8-sig")
            )


            st.download_button(
                label="Download Predictions CSV",
                data=csv_data,
                file_name="predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )


        except Exception as e:

            st.error(
                "An error occurred during analysis."
            )

            st.exception(e)