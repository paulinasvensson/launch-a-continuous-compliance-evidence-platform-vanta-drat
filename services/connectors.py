"""
Adapter interface for cloud/dev/HR provider connectors.

Real OAuth + provider APIs are out of scope for the MVP; each connector
generates realistic mock evidence payloads behind the same interface so the
sync pipeline and document generation work identically once real connectors
are swapped in later.
"""
from abc import ABC, abstractmethod


class BaseConnector(ABC):
    provider: str = "base"
    type: str = "cloud"

    @abstractmethod
    def fetch_evidence(self):
        """Return a list of dicts: {category, source_system, raw_data}."""
        raise NotImplementedError


class AWSConnector(BaseConnector):
    provider = "aws"
    type = "cloud"

    def fetch_evidence(self):
        return [
            {"category": "access_control", "source_system": "aws",
             "raw_data": {"iam_users": 14, "mfa_enabled_pct": 92}},
            {"category": "data_encryption", "source_system": "aws",
             "raw_data": {"s3_buckets_encrypted": True, "kms_keys": 6}},
            {"category": "logging", "source_system": "aws",
             "raw_data": {"cloudtrail_enabled": True, "retention_days": 365}},
        ]


class GCPConnector(BaseConnector):
    provider = "gcp"
    type = "cloud"

    def fetch_evidence(self):
        return [
            {"category": "access_control", "source_system": "gcp",
             "raw_data": {"iam_bindings": 20, "2fa_enforced": True}},
            {"category": "data_encryption", "source_system": "gcp",
             "raw_data": {"cmek_enabled": True, "buckets_encrypted": 18}},
        ]


class AzureConnector(BaseConnector):
    provider = "azure"
    type = "cloud"

    def fetch_evidence(self):
        return [
            {"category": "access_control", "source_system": "azure",
             "raw_data": {"aad_users": 30, "conditional_access_policies": 4}},
            {"category": "logging", "source_system": "azure",
             "raw_data": {"activity_log_retention_days": 90}},
        ]


class GitHubConnector(BaseConnector):
    provider = "github"
    type = "dev"

    def fetch_evidence(self):
        return [
            {"category": "code_change_control", "source_system": "github",
             "raw_data": {"branch_protection_enabled": True, "required_reviews": 2}},
            {"category": "vulnerability_scanning", "source_system": "github",
             "raw_data": {"dependabot_alerts_open": 3, "secret_scanning": True}},
            {"category": "model_versioning", "source_system": "github",
             "raw_data": {"ml_model_repo_tags": ["v1.2.0", "v1.3.0"]}},
        ]


class GitLabConnector(BaseConnector):
    provider = "gitlab"
    type = "dev"

    def fetch_evidence(self):
        return [
            {"category": "code_change_control", "source_system": "gitlab",
             "raw_data": {"merge_request_approvals_required": 1}},
            {"category": "vulnerability_scanning", "source_system": "gitlab",
             "raw_data": {"sast_enabled": True, "open_vulnerabilities": 5}},
        ]


class BambooHRConnector(BaseConnector):
    provider = "bamboohr"
    type = "hr"

    def fetch_evidence(self):
        return [
            {"category": "employee_training", "source_system": "bamboohr",
             "raw_data": {"ai_act_training_completion_pct": 78}},
            {"category": "access_offboarding", "source_system": "bamboohr",
             "raw_data": {"offboarded_last_90_days": 4, "access_revoked_on_time_pct": 100}},
        ]


class RipplingConnector(BaseConnector):
    provider = "rippling"
    type = "hr"

    def fetch_evidence(self):
        return [
            {"category": "employee_training", "source_system": "rippling",
             "raw_data": {"privacy_training_completion_pct": 85}},
            {"category": "access_offboarding", "source_system": "rippling",
             "raw_data": {"offboarded_last_90_days": 2, "access_revoked_on_time_pct": 100}},
        ]


CONNECTOR_REGISTRY = {
    "aws": AWSConnector,
    "gcp": GCPConnector,
    "azure": AzureConnector,
    "github": GitHubConnector,
    "gitlab": GitLabConnector,
    "bamboohr": BambooHRConnector,
    "rippling": RipplingConnector,
}


def get_connector(provider: str) -> BaseConnector:
    key = (provider or "").lower()
    cls = CONNECTOR_REGISTRY.get(key)
    if not cls:
        raise ValueError(f"unsupported provider: {provider}")
    return cls()
