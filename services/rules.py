"""
Static rules table mapping an organization's profile to applicable
requirements. Kept as data (not hardcoded per-endpoint) so it can be
updated as EU AI Act guidance and the US state privacy patchwork evolve.
"""

EU_AI_ACT_RULES = [
    {
        "framework": "EU AI Act",
        "jurisdiction": "EU",
        "requirement_text": "Article 11 - Maintain technical documentation demonstrating "
                             "compliance for the AI system before it is placed on the market.",
        "section_name": "System Overview & Intended Purpose",
        "condition": lambda org: org.sells_to_eu,
    },
    {
        "framework": "EU AI Act",
        "jurisdiction": "EU",
        "requirement_text": "Article 9 - Establish and maintain a risk management system "
                             "throughout the AI system's lifecycle.",
        "section_name": "Risk Management System",
        "condition": lambda org: org.sells_to_eu,
    },
    {
        "framework": "EU AI Act",
        "jurisdiction": "EU",
        "requirement_text": "Article 10 - Ensure training, validation and testing data "
                             "governance and data quality practices are documented.",
        "section_name": "Data Governance",
        "condition": lambda org: org.sells_to_eu,
    },
    {
        "framework": "EU AI Act",
        "jurisdiction": "EU",
        "requirement_text": "Article 12 - Ensure automatic logging of events (record-keeping) "
                             "over the system's lifetime.",
        "section_name": "Record-Keeping & Logging",
        "condition": lambda org: org.sells_to_eu,
    },
    {
        "framework": "EU AI Act",
        "jurisdiction": "EU",
        "requirement_text": "Article 14 - Design the system to enable effective human oversight.",
        "section_name": "Human Oversight Measures",
        "condition": lambda org: org.sells_to_eu,
    },
]

# US state privacy laws effective/expanding 2025-2026, keyed by state code.
US_STATE_PRIVACY_RULES = {
    "CA": "California CCPA/CPRA - honor consumer opt-out of sale/share and automated decision-making rights.",
    "CO": "Colorado Privacy Act - conduct data protection assessments for profiling in furtherance of AI features.",
    "CT": "Connecticut CTDPA - provide opt-out rights for profiling with legal/similarly significant effects.",
    "VA": "Virginia VCDPA - honor consumer rights and complete data protection assessments for AI-driven profiling.",
    "UT": "Utah UCPA - maintain reasonable data security and honor consumer opt-out requests.",
    "OR": "Oregon OCPA - disclose use of AI in profiling and honor opt-out of profiling requests.",
    "TX": "Texas TDPSA - conduct data protection assessments and disclose sale of sensitive/biometric data.",
    "MT": "Montana MCDPA - honor opt-out rights for targeted advertising and profiling.",
    "DE": "Delaware DPDPA (2025) - conduct data protection assessments for automated decision-making.",
    "IA": "Iowa ICDPA (2025) - honor consumer rights requests within statutory timelines.",
    "NE": "Nebraska NDPA (2025) - honor opt-out of sale of data used to train AI models.",
    "NH": "New Hampshire NHDPA (2025) - conduct assessments for profiling with legal effects.",
    "NJ": "New Jersey NJDPA (2025) - disclose AI-driven profiling and honor opt-out rights.",
    "MN": "Minnesota MCDPA (2025) - provide right to question/appeal automated decisions.",
    "MD": "Maryland MODPA (2025) - minimize collection and restrict sale of sensitive data used in AI features.",
}


def applicable_state_rules(states_csv: str):
    states = [s.strip().upper() for s in (states_csv or "").split(",") if s.strip()]
    return [(s, US_STATE_PRIVACY_RULES[s]) for s in states if s in US_STATE_PRIVACY_RULES]
