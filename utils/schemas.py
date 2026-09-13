from typing import Literal
from pydantic import BaseModel, Field


IssueLabel = Literal[
    "No Issue",
    "Ambiguity",
    "Incompleteness",
    "Inconsistency",
    "Duplication",
    "Conflict",
    "Non-verifiable",
]

Severity = Literal[
    "None",
    "Minor",
    "Major",
    "Critical",
]


class Requirement(BaseModel):
    id: str
    text: str


class ExtractionResult(BaseModel):
    requirements: list[Requirement]


class QualityAnalysis(BaseModel):
    requirement_id: str
    issue_label: IssueLabel
    severity: Severity
    explanation: str
    evidence: str


class QualityAnalysisResult(BaseModel):
    analyses: list[QualityAnalysis]


class RelationshipIssue(BaseModel):
    requirement_id: str
    related_requirement_id: str
    issue_label: Literal[
        "No Issue",
        "Inconsistency",
        "Duplication",
        "Conflict",
    ]
    severity: Severity
    explanation: str
    evidence: str


class RelationshipAnalysisResult(BaseModel):
    issues: list[RelationshipIssue]


class Recommendation(BaseModel):
    requirement_id: str
    recommendation: str
    improved_requirement: str
    sources: list[str] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    recommendations: list[Recommendation]


class FinalRequirementResult(BaseModel):
    requirement_id: str
    requirement: str
    issue_label: IssueLabel
    severity: Severity
    explanation: str
    evidence: str
    recommendation: str
    improved_requirement: str
    sources: list[str] = Field(default_factory=list)