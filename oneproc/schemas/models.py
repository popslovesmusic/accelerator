from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkerResult(BaseModel):
    agent_name: str
    command: List[str]
    cwd: str
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    git_diff: Optional[str] = None
    changed_files: List[str] = Field(default_factory=list)
    rollback_notes: Optional[str] = None

class EvidenceMetadata(BaseModel):
    model_classes_count: int
    seeds_used: int
    observables: List[str]
    normalization_method: str
    cross_model_comparison: str
    falsification_run: bool
    falsification_result: str
    recoverable_output_paths: List[str]

class LexiconTermCheck(BaseModel):
    term: str
    role: str
    registry_status: str
    classification: str
    allowed_claim_usage: str

class GateChecks(BaseModel):
    template_pass: bool
    lexicon_pass: bool
    measurement_pass: bool
    falsification_pass: bool
    multi_mechanism_pass: bool
    multi_seed_pass: bool
    cpp_preference_pass: bool
    language_policy_pass: bool
    provenance_pass: bool

class ClaimGateResult(BaseModel):
    claim_id: str
    requested_level: str
    final_level: str
    gate_result: str # pass | downgrade | block
    checks: GateChecks
    downgrades_applied: List[str] = Field(default_factory=list)
    blocked_reasons: List[str] = Field(default_factory=list)
    required_next_actions: List[str] = Field(default_factory=list)

class TemplateValidationResult(BaseModel):
    is_valid: bool
    missing_sections: List[str] = Field(default_factory=list)
    language_violations: List[str] = Field(default_factory=list)
    consistency_errors: List[str] = Field(default_factory=list)
