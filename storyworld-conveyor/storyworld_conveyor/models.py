from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AllowedAction:
    id: str
    label: str
    state_deltas: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class EncounterRecord:
    encounter_id: str
    family: str
    difficulty_tier: str
    title: str
    encounter_spec: str
    canonical_state: Dict[str, Any]
    allowed_actions: List[AllowedAction]
    constraints: List[str]
    required_mentions: List[str] = field(default_factory=list)
    forbidden_terms: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    target_action_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["allowed_actions"] = [asdict(item) for item in self.allowed_actions]
        return payload


@dataclass
class CompletionRecord:
    run_id: str
    stage_id: str
    encounter_id: str
    completion_id: str
    model_name: str
    model_provider: str
    completion_index: int
    prompt_path: str
    raw_prompt: str
    completion_text: str
    token_counts: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TraceRecord:
    run_id: str
    stage_id: str
    encounter_id: str
    completion_id: str
    completion_index: int
    model_name: str
    model_provider: str
    provider: str
    api_base: str
    system_prompt_path: str
    system_prompt: str
    prompt_path: str
    raw_output_path: str
    raw_prompt: str
    completion_text: str
    assistant_content: str
    reasoning_content: str
    finish_reason: str
    token_counts: Dict[str, int]
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EnvGradeRecord:
    run_id: str
    stage_id: str
    encounter_id: str
    completion_id: str
    action_validity: int
    constraint_violations: int
    target_count: int
    target_hits: int
    state_delta_count: int
    success_flag: int
    penalties: float
    env_score: float
    normalized: Dict[str, float]
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class JudgeRecord:
    run_id: str
    stage_id: str
    encounter_id: str
    completion_id: str
    judge_provider: str
    judge_model: str
    coherence: float
    ethical_adequacy: float
    least_bad_tradeoff_quality: float
    stakeholder_awareness: float
    uncertainty_handling: float
    concise_reasoning_quality: float
    judge_score: float
    raw_output_path: str
    system_prompt_path: str = ""
    system_prompt: str = ""
    prompt_path: str = ""
    raw_prompt: str = ""
    response_text: str = ""
    reasoning_content: str = ""
    finish_reason: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AggregateRecord:
    run_id: str
    stage_id: str
    encounter_id: str
    completion_id: str
    env_score: float
    judge_score: float
    final_score: float
    env_weight: float
    judge_weight: float
    rank_within_encounter: int
    bundle: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Manifest:
    run_id: str
    stage: str
    status: str
    started_at: str
    completed_at: Optional[str]
    input_files: List[str]
    output_files: List[str]
    counters: Dict[str, Any]
    config_digest: str
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
