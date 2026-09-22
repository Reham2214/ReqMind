import pandas as pd
import streamlit as st

from graph import graph
from utils.file_parser import extract_text


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="ReqMind",
    page_icon="",
    layout="wide",
)


# ==========================================================
# Session State
# ==========================================================

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []

if "analysis_completed" not in st.session_state:
    st.session_state.analysis_completed = False


# ==========================================================
# Header
# ==========================================================

st.title("ReqMind")

st.write(
    "AI-powered software requirements analysis system"
)

st.divider()


# ==========================================================
# File Upload
# ==========================================================

st.subheader("Upload Requirements")

st.write(
    "Upload a PDF, DOCX, TXT, or CSV file containing "
    "your software requirements."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=[
        "pdf",
        "docx",
        "txt",
        "csv",
    ],
)


# ==========================================================
# Analyze Uploaded File
# ==========================================================

if uploaded_file is not None:

    st.success(
        f"Uploaded file: {uploaded_file.name}"
    )

    if st.button(
        "Analyze Requirements",
        type="primary",
        use_container_width=True,
    ):

        try:

            # --------------------------------------------------
            # Reset Previous Results
            # --------------------------------------------------

            st.session_state.analysis_results = []
            st.session_state.analysis_completed = False

            # --------------------------------------------------
            # Read Uploaded File
            # --------------------------------------------------

            file_bytes = uploaded_file.getvalue()

            # --------------------------------------------------
            # CSV Handling
            # --------------------------------------------------

            if uploaded_file.name.lower().endswith(".csv"):

                csv_df = pd.read_csv(
                    uploaded_file
                )

                if "Requirement" not in csv_df.columns:

                    st.error(
                        "CSV file must contain a 'Requirement' column."
                    )

                    st.stop()

                requirement_lines = []

                for index, row in csv_df.iterrows():

                    requirement_text = str(
                        row["Requirement"]
                    ).strip()

                    if not requirement_text:
                        continue

                    if "ID" in csv_df.columns:

                        requirement_id = str(
                            row["ID"]
                        ).strip()

                        requirement_lines.append(
                            f"{requirement_id}: {requirement_text}"
                        )

                    else:

                        requirement_lines.append(
                            requirement_text
                        )

                document_text = "\n".join(
                    requirement_lines
                )

            # --------------------------------------------------
            # PDF / DOCX / TXT Handling
            # --------------------------------------------------

            else:

                document_text = extract_text(
                    uploaded_file.name,
                    file_bytes,
                )

            # --------------------------------------------------
            # Validate Extracted Text
            # --------------------------------------------------

            if not document_text.strip():

                st.error(
                    "No readable requirements were found "
                    "in the uploaded file."
                )

                st.stop()

            # --------------------------------------------------
            # Analysis Progress
            # --------------------------------------------------

            st.subheader(
                "Analysis Progress"
            )

            extraction_status = st.empty()

            quality_status = st.empty()

            relationship_status = st.empty()

            recommendation_status = st.empty()

            extraction_status.info(
                "1. Extracting requirements..."
            )

            quality_status.info(
                "2. Quality Analysis — waiting..."
            )

            relationship_status.info(
                "3. Relationship Analysis — waiting..."
            )

            recommendation_status.info(
                "4. Recommendations & Knowledge Retrieval — waiting..."
            )

            # --------------------------------------------------
            # Run ReqMind
            # --------------------------------------------------

            final_results = []

            for update in graph.stream(
                {
                    "document_text": document_text
                },
                stream_mode="updates",
            ):

                # ----------------------------------------------
                # Extraction
                # ----------------------------------------------

                if "extraction" in update:

                    extraction_status.success(
                        "1. Extraction completed"
                    )

                    quality_status.info(
                        "2. Quality Analysis — running..."
                    )

                    relationship_status.info(
                        "3. Relationship Analysis — running..."
                    )

                # ----------------------------------------------
                # Quality Analysis
                # ----------------------------------------------

                if "quality_analysis" in update:

                    quality_status.success(
                        "2. Quality Analysis completed"
                    )

                # ----------------------------------------------
                # Relationship Analysis
                # ----------------------------------------------

                if "relationship_analysis" in update:

                    relationship_status.success(
                        "3. Relationship Analysis completed"
                    )

                # ----------------------------------------------
                # Recommendations
                # ----------------------------------------------

                if "recommendation" in update:

                    recommendation_status.success(
                        "4. Recommendations & Knowledge Retrieval completed"
                    )

                    final_results = update[
                        "recommendation"
                    ].get(
                        "final_results",
                        [],
                    )

            # --------------------------------------------------
            # Save Results
            # --------------------------------------------------

            st.session_state.analysis_results = (
                final_results
            )

            st.session_state.analysis_completed = True

            st.success(
                "Analysis completed successfully."
            )

        except Exception as e:

            st.error(
                f"Analysis failed: {e}"
            )


# ==========================================================
# Analysis Results
# ==========================================================

results = st.session_state.analysis_results


if (
    st.session_state.analysis_completed
    and results
):

    st.divider()

    st.subheader(
        f"Analysis Results ({len(results)} Requirements)"
    )

    # ------------------------------------------------------
    # Summary Metrics
    # ------------------------------------------------------

    total_requirements = len(
        results
    )

    issues_detected = sum(
        1
        for result in results
        if result.issue_label != "No Issue"
    )

    no_issues = sum(
        1
        for result in results
        if result.issue_label == "No Issue"
    )
    from collections import Counter

    issue_counts = Counter(
       result.issue_label
        for result in results
       )

    st.subheader("Issue Distribution")
    st.write(dict(issue_counts))

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Requirements",
            total_requirements,
        )

    with col2:

        st.metric(
            "Issues Detected",
            issues_detected,
        )

    with col3:

        st.metric(
            "No Issues",
            no_issues,
        )

    st.divider()

    # ------------------------------------------------------
    # Requirement Selector
    # ------------------------------------------------------

    requirement_options = [
        (
            f"{result.requirement_id} — "
            f"{result.requirement}"
        )
        for result in results
    ]

    selected_requirement = st.selectbox(
        "Select a requirement",
        requirement_options,
    )

    selected_index = (
        requirement_options.index(
            selected_requirement
        )
    )

    selected_result = results[
        selected_index
    ]

    # ------------------------------------------------------
    # Selected Requirement
    # ------------------------------------------------------

    st.subheader(
        selected_result.requirement_id
    )

    st.write(
        "### Requirement"
    )

    st.info(
        selected_result.requirement
    )

    # ------------------------------------------------------
    # Issue + Severity
    # ------------------------------------------------------

    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.write(
            "**Issue**"
        )

        st.write(
            selected_result.issue_label
        )

    with result_col2:

        st.write(
            "**Severity**"
        )

        st.write(
            selected_result.severity
        )

    st.divider()

    # ------------------------------------------------------
    # Explanation
    # ------------------------------------------------------

    st.write(
        "### Explanation"
    )

    st.write(
        selected_result.explanation
    )

    # ------------------------------------------------------
    # Evidence
    # ------------------------------------------------------

    st.write(
        "### Evidence"
    )

    if selected_result.evidence:

        st.write(
            selected_result.evidence
        )

    else:

        st.write(
            "No specific evidence provided."
        )

    # ------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------

    st.write(
        "### Recommendation"
    )

    st.write(
        selected_result.recommendation
    )

    # ------------------------------------------------------
    # Improved Requirement
    # ------------------------------------------------------

    st.write(
        "### Improved Requirement"
    )

    st.success(
        selected_result.improved_requirement
    )

    # ------------------------------------------------------
    # Knowledge Sources
    # ------------------------------------------------------

    st.write(
        "### Knowledge Sources"
    )

    if selected_result.sources:

        for source in selected_result.sources:

            st.write(
                f"- {source}"
            )

    else:

        st.write(
            "No knowledge sources were retrieved."
        )

    # ======================================================
    # Download Results
    # ======================================================

    st.divider()

    st.subheader(
        "Download Analysis Results"
    )

    st.write(
        "Export the complete analysis as a CSV file "
        "for easy review, sharing, documentation, "
        "and further processing."
    )

    # ------------------------------------------------------
    # Prepare Download Data
    # ------------------------------------------------------

    download_data = []

    for result in results:

        download_data.append(
            {
                "Requirement ID": result.requirement_id,
                "Requirement": result.requirement,
                "Issue Label": result.issue_label,
                "Severity": result.severity,
                "Explanation": result.explanation,
                "Evidence": result.evidence,
                "Recommendation": result.recommendation,
                "Improved Requirement": result.improved_requirement,
                "Sources": ", ".join(
                    result.sources
                ),
            }
        )

    download_df = pd.DataFrame(
        download_data
    )

    csv_data = download_df.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        label="Download Analysis Results",
        data=csv_data,
        file_name="reqmind_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )