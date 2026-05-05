# Domain Router Lattice

Use this reference when a task should be specialized by broad subject/cognition type before authoring a final MeTTa/TRM package.

The router is deliberately broader than final Hermes skills. It should select a reusable domain adapter, then let `AUTHOR -> REPAIR -> VERIFY -> EXPORT_ROWS` produce the concrete task packet.

## Domains

- `formal_reasoning`: mathematics, logic, proofs, invariants, symbolic search, contradiction tests.
- `empirical_science`: hypothesis formation, experimental design, measurement, ablation, causal evidence.
- `systems_engineering`: architecture, interfaces, control loops, reliability, optimization, integration.
- `biosocial_ecology`: living systems, ALife, adaptation, agents, ecology, social dynamics.
- `social_governance`: law, institutions, incentives, diplomacy, coalitions, legitimacy, policy.
- `humanities_interpretive`: texts, history, theology, philosophy, motifs, meaning, hermeneutics.
- `creative_narrative`: storyworlds, characters, encounter DAGs, player values, secret endings.
- `safety_security`: red-team gyms, tamper sensing, anomaly detection, containment, escalation gates.
- `tool_operations`: repo navigation, tool calls, JSON contracts, shell-safe plans, workflow execution.
- `metacognition_learning`: curriculum design, skill improvement, verifier feedback, memory, self-evaluation.

## Router Output

Emit a compact JSON object:

```json
{
  "domain_id": "formal_reasoning",
  "confidence": 0.82,
  "cognitive_modes": ["proof", "symbolic_search"],
  "task_focus": "short phrase",
  "routing_reason": "short phrase"
}
```

## Domain Adapter Rule

Build the package task from the prompt, selected domain, and cognitive modes. Keep the target env generic, e.g. `domain_formal_reasoning`, unless the caller provides a benchmark env.

Every domain task should still produce the same package files:

- `package.manifest.json`
- `package.metta`
- `contracts.metta`
- `retrieval_policy.metta`
- `failure_modes.metta`
- `examples/minimal_valid.json`

## Evaluation

Report these separately:

- Router accuracy against hand-labeled broad domains.
- Raw bootstrap score from the small model.
- Repaired bootstrap score after deterministic MeTTa repair.
- Runtime-ready rate.
- Repair-controller exact action rate, if repair rows are exported.

Do not treat high repaired score as proof the LLM routed correctly. Routing, authoring, repair, and controller decisions are separate capabilities.
