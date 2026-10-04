"""
Pluggable integration adapters. Each adapter simulates an OAuth-based evidence
pull from a provider and returns a list of structured evidence dicts.
New providers can be added here without touching the Integration schema.
"""
from datetime import datetime


def _aws_adapter(org, integration):
    return [
        {"type": "config", "content_ref": "AWS IAM policy snapshot: least-privilege roles enforced for ML pipeline."},
        {"type": "log", "content_ref": "AWS CloudTrail: model inference endpoint access logs (30d retention)."},
    ]


def _gcp_adapter(org, integration):
    return [
        {"type": "config", "content_ref": "GCP IAM audit: Vertex AI dataset access restricted to ML team."},
    ]


def _azure_adapter(org, integration):
    return [
        {"type": "config", "content_ref": "Azure Policy: encryption-at-rest enforced on storage accounts hosting training data."},
    ]


def _github_adapter(org, integration):
    return [
        {"type": "log", "content_ref": "GitHub: branch protection + required review enabled on model-serving repo."},
        {"type": "config", "content_ref": "GitHub Actions: CI pipeline includes model evaluation/test gate before deploy."},
    ]


def _bamboohr_adapter(org, integration):
    return [
        {"type": "attestation", "content_ref": "BambooHR: AI acceptable-use policy acknowledged by 100% of employees."},
    ]


def _rippling_adapter(org, integration):
    return [
        {"type": "attestation", "content_ref": "Rippling: data protection training completion records for all staff."},
    ]


PROVIDER_ADAPTERS = {
    "aws": _aws_adapter,
    "gcp": _gcp_adapter,
    "azure": _azure_adapter,
    "github": _github_adapter,
    "bamboohr": _bamboohr_adapter,
    "rippling": _rippling_adapter,
}


def pull_evidence(provider, org, integration):
    adapter = PROVIDER_ADAPTERS.get(provider)
    if adapter is None:
        return []
    return adapter(org, integration)
