import io
from collections import Counter

import pandas as pd
import streamlit as st
import plotly.express as px

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)

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
# Custom Styling
# ==========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .reqmind-header {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            #172554 0%,
            #1e3a8a 50%,
            #2563eb 100%
        );
        color: white;
        margin-bottom: 1.5rem;
    }

    .reqmind-header h1 {
        margin-bottom: 0.3rem;
        font-size: 2.2rem;
    }

    .reqmind-header p {
        margin: 0;
        opacity: 0.9;
        font-size: 1rem;
    }

    .metric-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    .section-card {
        background: white;
        padding: 1.3rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }

    .issue-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 0.5rem;
        line-height: 1.2;
    }

    .severity-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background-color: #eef2ff;
        color: #3730a3;
        font-weight: 600;
        font-size: 0.9rem;
        line-height: 1.2;
    }

    .requirement-box {
        background-color: #f8fafc;
        border-left: 5px solid #2563eb;
        padding: 1rem 1.1rem;
        border-radius: 8px;
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #0f172a;
    }

    .recommendation-box {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 1rem 1.1rem;
        border-radius: 8px;
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #0f172a;
    }

    .improved-box {
        background-color: #f0fdf4;
        border-left: 5px solid #16a34a;
        padding: 1rem 1.1rem;
        border-radius: 8px;
        line-height: 1.6;
        color: #0f172a;
    }

    .source-box {
        background-color: transparent;
        border: none;
        padding: 0;
        border-radius: 0;
        margin-bottom: 0.5rem;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
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

st.markdown(
    """
    <div class="reqmind-header">
        <h1>ReqMind</h1>
        <p>
            AI-powered software requirements analysis system
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


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
# PDF Generator
# ==========================================================

def create_pdf(results):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReqMindTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "ReqMindSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReqMindHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "ReqMindBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=8,
    )

    small_style = ParagraphStyle(
        "ReqMindSmall",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=12,
        textColor=colors.grey,
    )

    story = []

    story.append(
        Paragraph(
            "ReqMind",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Improved Software Requirements Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Total analyzed requirements: {len(results)}",
            body_style,
        )
    )

    story.append(Spacer(1, 8))

    for index, result in enumerate(results):

        story.append(
            Paragraph(
                f"Requirement {result.requirement_id}",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                "<b>Original Requirement</b>",
                body_style,
            )
        )

        story.append(
            Paragraph(
                str(result.requirement).replace(
                    "&",
                    "&amp;"
                ).replace(
                    "<",
                    "&lt;"
                ).replace(
                    ">",
                    "&gt;"
                ),
                body_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Classification:</b> "
                f"{result.issue_label}",
                body_style,
            )
        )

        story.append(
            Paragraph(
                f"<b>Severity:</b> "
                f"{result.severity}",
                body_style,
            )
        )

        story.append(
            Paragraph(
                "<b>Recommendation</b>",
                body_style,
            )
        )

        story.append(
            Paragraph(
                str(result.recommendation).replace(
                    "&",
                    "&amp;"
                ).replace(
                    "<",
                    "&lt;"
                ).replace(
                    ">",
                    "&gt;"
                ),
                body_style,
            )
        )

        story.append(
            Paragraph(
                "<b>Improved Requirement</b>",
                body_style,
            )
        )

        story.append(
            Paragraph(
                str(
                    result.improved_requirement
                ).replace(
                    "&",
                    "&amp;"
                ).replace(
                    "<",
                    "&lt;"
                ).replace(
                    ">",
                    "&gt;"
                ),
                body_style,
            )
        )

        if result.sources:

            story.append(
                Paragraph(
                    "<b>Knowledge Sources</b>",
                    body_style,
                )
            )

            for source in result.sources:

                story.append(
                    Paragraph(
                        f"• {str(source)}",
                        small_style,
                    )
                )

        if index < len(results) - 1:

            story.append(
                PageBreak()
            )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


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
        "ReqMind Dashboard"
    )

    # ------------------------------------------------------
    # Summary Calculations
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

    issue_counts = Counter(
        result.issue_label
        for result in results
    )

    issue_percentage = (
        (issues_detected / total_requirements) * 100
        if total_requirements
        else 0
    )

    no_issue_percentage = (
        (no_issues / total_requirements) * 100
        if total_requirements
        else 0
    )

    # ------------------------------------------------------
    # Dashboard Metrics
    # ------------------------------------------------------

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:

        st.metric(
            "Extracted Requirements",
            total_requirements,
        )

    with metric_col2:

        st.metric(
            "Issues Detected",
            issues_detected,
            f"{issue_percentage:.1f}%"
        )

    with metric_col3:

        st.metric(
            "No Issues",
            no_issues,
            f"{no_issue_percentage:.1f}%"
        )

    with metric_col4:

        st.metric(
            "Issue Types",
            len(issue_counts),
        )

    st.divider()

    # ------------------------------------------------------
    # Issue Distribution
    # ------------------------------------------------------

    st.subheader(
        "Requirement Classification"
    )

    chart_col1, chart_col2 = st.columns(
        [1.5, 1]
    )

    chart_data = pd.DataFrame(
        {
            "Classification": list(
                issue_counts.keys()
            ),
            "Count": list(
                issue_counts.values()
            ),
        }
    )

    color_map = {
        "No Issue": "#22c55e",
        "Ambiguity": "#f59e0b",
        "Incompleteness": "#ef4444",
        "Non-verifiable": "#8b5cf6",
        "Duplication": "#3b82f6",
        "Conflict": "#dc2626",
        "Inconsistency": "#eab308",
    }

    with chart_col1:

        fig = px.bar(
            chart_data,
            x="Classification",
            y="Count",
            color="Classification",
            color_discrete_map=color_map,
            text="Count",
            title="Issues by Classification",
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
            xaxis_title="",
            yaxis_title="Number of Requirements",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with chart_col2:

        pie_fig = px.pie(
            chart_data,
            names="Classification",
            values="Count",
            hole=0.55,
            color="Classification",
            color_discrete_map=color_map,
            title="Overall Distribution",
        )

        pie_fig.update_layout(
            height=400,
            margin=dict(
                l=10,
                r=10,
                t=60,
                b=10,
            ),
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True,
        )

    # ------------------------------------------------------
    # Classification Filter
    # ------------------------------------------------------

    st.subheader(
        "Explore Requirements"
    )

    filter_options = [
        "All Classifications"
    ] + sorted(
        issue_counts.keys()
    )

    selected_filter = st.selectbox(
        "Filter requirements by classification",
        filter_options,
    )

    if selected_filter == "All Classifications":

        filtered_results = results

    else:

        filtered_results = [
            result
            for result in results
            if result.issue_label == selected_filter
        ]

    # ------------------------------------------------------
    # Requirement Selector
    # ------------------------------------------------------

    requirement_options = [
        (
            f"{result.requirement_id} — "
            f"{result.requirement}"
        )
        for result in filtered_results
    ]

    if not requirement_options:

        st.info(
            "No requirements match the selected classification."
        )

    else:

        selected_requirement = st.selectbox(
            "Select a requirement",
            requirement_options,
        )

        selected_index = (
            requirement_options.index(
                selected_requirement
            )
        )

        selected_result = filtered_results[
            selected_index
        ]

        st.divider()

        # --------------------------------------------------
        # Selected Requirement
        # --------------------------------------------------

        st.subheader(
            selected_result.requirement_id
        )

        # --------------------------------------------------
        # Requirement
        # --------------------------------------------------

        st.write(
            "### Requirement"
        )

        st.markdown(
            f"""
            <div class="requirement-box">
                {selected_result.requirement}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        st.write(
            "### Classification"
        )

        issue_color = color_map.get(
            selected_result.issue_label,
            "#64748b",
        )

        st.markdown(
            f"""
            <span
                class="issue-badge"
                style="
                    background-color: {issue_color}20;
                    color: {issue_color};">
                {selected_result.issue_label}
            </span>
            

            <span class="severity-badge">
                Severity: {selected_result.severity}
            </span>
            """,
            unsafe_allow_html=True,
        )

        # --------------------------------------------------
        # Explanation
        # --------------------------------------------------

        st.write(
            "### Explanation"
        )

        st.write(
            selected_result.explanation
        )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        st.write(
            "### Evidence"
        )

        if selected_result.evidence:

            st.info(
                selected_result.evidence
            )

        else:

            st.write(
                "No specific evidence provided."
            )

        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        st.write(
            "### Recommendation"
        )

        st.markdown(
            f"""
            <div class="recommendation-box">
                {selected_result.recommendation}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --------------------------------------------------
        # Improved Requirement
        # --------------------------------------------------

        st.write(
            "### Improved Requirement"
        )

        st.markdown(
            f"""
            <div class="improved-box">
                {selected_result.improved_requirement}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --------------------------------------------------
        # Knowledge Sources
        # --------------------------------------------------

        st.write(
            "### Knowledge Base / Sources"
        )

        if selected_result.sources:

            for source in selected_result.sources:

                st.markdown(
                    f"""
                    <div class="source-box">
                        {source}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.write(
                "No knowledge sources were retrieved."
            )

    # ======================================================
    # PDF Export
    # ======================================================

    st.divider()

    st.subheader(
        "Export Improved Requirements"
    )

    st.write(
        "Download a PDF containing the analyzed requirements, "
        "classifications, recommendations, and improved requirements."
    )

    all_results_for_pdf = st.session_state.analysis_results

    pdf_data = create_pdf(
        all_results_for_pdf
    )

    st.download_button(
        label="Download Improved Requirements (PDF)",
        data=pdf_data,
        file_name="reqmind_improved_requirements.pdf",
        mime="application/pdf",
        use_container_width=True,
    )