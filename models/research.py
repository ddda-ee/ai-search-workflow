from pydantic import BaseModel
from typing import List


class ResearchPlan(BaseModel):

    research_goal: str

    research_questions: List[str]

    sub_questions: List[str]

    chinese_keywords: List[str]

    english_keywords: List[str]

    technology_routes: List[str]

    source_types: List[str]

def research_plan_schema() -> dict:

        return {
            "type": "object",

            "properties": {

                "research_goal": {
                    "type": "string"
                },

                "research_questions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "sub_questions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "chinese_keywords": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "english_keywords": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "technology_routes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },

                "source_types": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },

            "required": [
                "research_goal",
                "research_questions",
                "sub_questions",
                "chinese_keywords",
                "english_keywords",
                "technology_routes",
                "source_types"
            ],

            "additionalProperties": False
        }    

class SearchTask(BaseModel):

    question: str

    keywords: List[str]

    source_types: List[str]

    priority: str

    purpose: str

def search_task_schema() -> dict:

        return {
            "type": "object",

            "properties": {

                "tasks": {
                    "type": "array",

                    "items": {

                        "type": "object",

                        "properties": {

                            "question": {
                                "type": "string"
                            },

                            "keywords": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },

                            "source_types": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },

                            "priority": {
                                "type": "string"
                            },

                            "purpose": {
                                "type": "string"
                            }
                        },

                        "required": [
                            "question",
                            "keywords",
                            "source_types",
                            "priority",
                            "purpose"
                        ],

                        "additionalProperties": False
                    }
                }
            },

            "required": [
                "tasks"
            ],

            "additionalProperties": False
        }

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    published_at: str | None = None

class Document(BaseModel):
    title: str
    url: str
    content: str
    source: str
    published_at: str | None = None

class Finding(BaseModel):
    document_title: str
    document_url: str

    key_points: list[str]

    methods: list[str]

    datasets: list[str]

    evaluation_metrics: list[str]

    findings: list[str]

    limitations: list[str]

def finding_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "document_title": {
                "type": "string"
            },
            "document_url": {
                "type": "string"
            },
            "key_points": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "methods": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "datasets": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "evaluation_metrics": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "findings": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "limitations": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": [
            "document_title",
            "document_url",
            "key_points",
            "methods",
            "datasets",
            "evaluation_metrics",
            "findings",
            "limitations"
        ],
        "additionalProperties": False
    }

class DocumentChunk(BaseModel):
    document_title: str
    document_url: str
    chunk_id: int
    content: str

def merged_finding_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "document_title": {
                "type": "string"
            },
            "document_url": {
                "type": "string"
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            },
            "methods": {
                "type": "array",
                "items": {"type": "string"}
            },
            "datasets": {
                "type": "array",
                "items": {"type": "string"}
            },
            "evaluation_metrics": {
                "type": "array",
                "items": {"type": "string"}
            },
            "findings": {
                "type": "array",
                "items": {"type": "string"}
            },
            "limitations": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "document_title",
            "document_url",
            "key_points",
            "methods",
            "datasets",
            "evaluation_metrics",
            "findings",
            "limitations"
        ],
        "additionalProperties": False
    }

class Evidence(BaseModel):
    claim: str
    supported: bool
    evidence: str
    source_url: str
    reason: str

class FactCheckResult(BaseModel):
    document_title: str
    document_url: str
    evidences: list[Evidence]

def fact_check_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "document_title": {
                "type": "string"
            },
            "document_url": {
                "type": "string"
            },
            "evidences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {
                            "type": "string"
                        },
                        "supported": {
                            "type": "boolean"
                        },
                        "evidence": {
                            "type": "string"
                        },
                        "source_url": {
                            "type": "string"
                        },
                        "reason": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "claim",
                        "supported",
                        "evidence",
                        "source_url",
                        "reason"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "document_title",
            "document_url",
            "evidences"
        ],
        "additionalProperties": False
    }

class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    background: str
    research_status: list[str]
    key_methods: list[str]
    key_findings: list[str]
    comparison: list[str]
    limitations: list[str]
    research_gaps: list[str]
    future_directions: list[str]
    references: list[str]

def research_report_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "executive_summary": {"type": "string"},
            "background": {"type": "string"},
            "research_status": {
                "type": "array",
                "items": {"type": "string"}
            },
            "key_methods": {
                "type": "array",
                "items": {"type": "string"}
            },
            "key_findings": {
                "type": "array",
                "items": {"type": "string"}
            },
            "comparison": {
                "type": "array",
                "items": {"type": "string"}
            },
            "limitations": {
                "type": "array",
                "items": {"type": "string"}
            },
            "research_gaps": {
                "type": "array",
                "items": {"type": "string"}
            },
            "future_directions": {
                "type": "array",
                "items": {"type": "string"}
            },
            "references": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "title",
            "executive_summary",
            "background",
            "research_status",
            "key_methods",
            "key_findings",
            "comparison",
            "limitations",
            "research_gaps",
            "future_directions",
            "references"
        ],
        "additionalProperties": False
    }

class ReviewResult(BaseModel):
    passed: bool
    issues: list[str]
    suggestions: list[str]

def review_result_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "passed": {
                "type": "boolean"
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"}
            },
            "suggestions": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "passed",
            "issues",
            "suggestions"
        ],
        "additionalProperties": False
    }





