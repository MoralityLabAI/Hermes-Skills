# TRM-MCP: Tiny Recursive Controllers for Structured Tool Memory

Patrick Dugan, Morality Lab

## Abstract

Model Context Protocol surfaces expose tools, resources, templates, and structured memory, but a small model can waste most of its context budget repeatedly scanning the same lookup surface. We propose TRM-MCP: a decomposition that trains Tiny Recursive Models to choose where to look, which handle or template to use, whether retrieved evidence is relevant, and when to stop. The current artifact set includes a generic MCP trace matrix across filesystem, GitHub, and Postgres surfaces with `15` traces and `42` route/retrieve/verify rows, plus a storyworld play-diary MCP environment study over `15` scenarios and `20` plays. In the storyworld study, diary-aided NAV raised average lift to `+0.619333` and removed four negative-NAV cases by letting retrieved outcome evidence override a brittle current-turn policy. These results motivate a concrete research program: train small TRM controllers to emit retrieval pointers and stop/escalate decisions over structured MCP memory, optimizing answer quality per token rather than raw answer quality alone.

## Thesis

The core claim is that MCP should not be treated as a giant text context. It should be treated as an addressable memory surface.

The TRM does not need to know the contents of the filesystem, repository, database, play diary, or storyworld index. It needs to learn a compact policy:

1. Which MCP family should be queried?
2. Which URI, template, entity, or handle is likely relevant?
3. Is the selected resource an exact hit, a near miss, wrong scope, or wrong family?
4. Has enough evidence been retrieved?
5. Should the system stop, continue, or escalate?

This makes TRM-MCP a control-plane architecture rather than a knowledge-distillation architecture. The TRM outputs pointers and actions, not prose answers.

## Architecture

TRM-MCP decomposes lookup into four roles:

1. Index TRM: compresses resource labels, URIs, parameter names, and query cues into family labels and answer-shape tags.
2. Router TRM: maps a user query and prior failure notes to an MCP family and lookup mode.
3. Retriever TRM: chooses the best URI, template, or parameter sketch from candidates.
4. Verifier TRM: rejects near misses, wrong-scope resources, and wrong-family matches.

The deterministic MCP executor remains outside the model. It lists resources, reads resources, expands templates, and enforces token budgets. The main LLM receives a small evidence bundle, not the full MCP surface.

## Generic Example Matrix

The current generic example matrix covers three MCP-like surfaces:

1. filesystem,
2. GitHub,
3. Postgres.

Each pack has five traces and fourteen TRM rows. The merged matrix has:

1. `15` traces,
2. `42` rows,
3. `15` route rows,
4. `12` retrieve rows,
5. `15` verify rows,
6. `36` exact-positive rows,
7. `6` negative rows.

These traces are designed to exercise exact lookup and hard negatives: semantically attractive resources that should be rejected because the scope, family, or answer shape is wrong.

This is a training-corpus seed, not a final benchmark. Its immediate value is schema design: it defines the row families, labels, negatives, and action surfaces needed to train and evaluate TRM-MCP controllers.

## DB Lookup Efficiency Model

The Postgres worked example motivates an efficiency graph for naive broad lookup versus typed TRM-MCP lookup. The graph is a bounded analytical model, not a measured latency benchmark. It compares a broad list-then-read workflow against direct resource-handle or template retrieval.

For exact schema reads, the naive workflow is modelled as: list schema groups, list candidate relations, then read the selected relation. The TRM-MCP workflow is modelled as: route directly to the expected resource handle and read it. This reduces modelled MCP calls from `3` to `1` and lookup units from `6` to `2`.

For query-template reads, the naive workflow is modelled as: list templates, inspect plausible candidates, then instantiate or read the selected template. The TRM-MCP workflow uses a direct template handle. This reduces modelled MCP calls from `3` to `1` and lookup units from `5` to `2`.

The Postgres pack also includes two failure cases: a wrong-table near miss and a wrong-route schema lookup. In TRM-MCP terms these are not merely failures; they are verifier training rows. The paper should use this as a schema-control argument: a useful DB lookup controller must reject attractive wrong resources before they waste downstream context.

## MeTTa Schema-Surface Enrichment

A separate Primehub schema MCP pack extends the same idea from SQL-style relation lookup to benchmark schema lookup. The generated surface covers three structured environments: `psycho_bench`, `ascii_tree`, and `pydantic_adherence`.

The MeTTa/MCP-enriched schema surface contains:

1. `6` stable resource handles,
2. `6` answer-shape tags,
3. `6` query-cue sets,
4. `6` minimal examples,
5. `6` failure-mode sets,
6. `2` validation-path or validator-note enriched resources,
7. `6` source replay links.

This is the concrete meaning of "MeTTa improves the DB schema" in the current evidence: it turns vague prompt and replay material into addressable schema records with handles, answer shapes, cues, examples, failure modes, and verifier notes. It is not yet a live SQL migration claim.

## Recovered Live Schema-Retrieval Measurement

The April Primehub structured-map retrieval study contains a live 9B measurement that should be treated as the primary empirical result for this paper seed's schema-memory claim.

The run compares three arms:

1. `baseline`: no Hermes structured-map prompt.
2. `plain_structured_map`: the structured-map skill prompt without retrieved schema memory.
3. `retrieval_assisted`: the structured-map prompt plus TRM-MCP-style Primehub schema memory.

The post-fix three-environment snapshot reports:

1. `ascii_tree`: baseline `0.0`, plain structured-map `0.0`, retrieval-assisted `0.8`.
2. `psycho_bench`: baseline `3.3283`, plain structured-map `3.3061`, retrieval-assisted `3.3311`.
3. `pydantic_adherence`: baseline `0.0`, plain structured-map `0.0`, retrieval-assisted `1.0`.

Token usage shows why the claim must be precise. Retrieval-assisted schema memory did not reduce prompt tokens in this implementation. It increased total tokens from `497` to `939` on `ascii_tree`, from `1119` to `1534` on `psycho_bench`, and from `1243` to `1860` on `pydantic_adherence`. The measured win is therefore not "retrieval is cheaper in this prompt implementation." The win is "retrieved schema memory buys exact structured validity in lanes where naive prompting fails."

This is still an efficiency result in a capability sense: for `ascii_tree` and `pydantic_adherence`, the baseline spent fewer tokens but achieved zero reward. The retrieval-assisted arm spent more tokens but crossed the validity threshold. For `psycho_bench`, where the baseline already performs well, retrieval is not token-efficient and should not be promoted as a universal improvement.

## Storyworld Play-Diary MCP

The storyworld player adds episodic memory. Repeated playthroughs write a play diary containing episode summaries, turn rows, legal actions, selected actions, NAV recommendations, endings, scores, and TRM labels.

The play-diary MCP exposes lookup and export flows:

1. `--use-play-diary`: retrieve prior turns before each action prompt.
2. `--write-play-diary`: ingest completed plays into memory.
3. `--num-plays N`: let play `N+1` use rows written by play `N`.
4. `--diary-top-k K`: keep lookup context compact.
5. `export-trm`: emit reduced TRM examples.

The contract is strict: diary evidence is subordinate to current legal actions. A retrieved action must not be copied unless it appears in the current legal-action set.

## Storyworld Environment Study

The `overnight_policy_v2` run used the `paper` profile with `15` scenarios, `20` plays, max depth `7`, and branch limit `1024`.

The v2 diary policy seeds MCP memory with deterministic and NAV rollouts, then lets retrieved outcome evidence override NAV when a remembered legal action has a better score. Average diary lift reached `+0.619333`.

The most interpretable wins:

1. `market_square`: diary lift `+4.4`.
2. `medicine_dilemma`: diary lift `+1.4`.
3. `multi_agent_release_council`: diary lift `+1.64`.
4. `scarlett_letter`: diary lift `+1.85`.

The clearest safety-style result is not only positive lift. It is recovery from bad NAV guidance:

1. `bitcoin_consensus_oversight`: NAV lift `-0.25`, diary lift `0.0`.
2. `decentralized_ai_governance`: NAV lift `-0.1`, diary lift `0.0`.
3. `distributed_atomspace_negotiation`: NAV lift `-0.5`, diary lift `0.0`.
4. `quantum_signal_fusion`: NAV lift `-1.52`, diary lift `0.0`.

In these cases, diary memory acts as a correction layer: prior outcome evidence prevents a brittle current policy from pushing below baseline.

## Training Target

TRM-MCP training rows should be state-to-retrieval-policy examples, not question-to-answer examples.

A minimal row should include:

1. task text,
2. compact task state,
3. available MCP families,
4. candidate descriptors,
5. gold route or URI/template,
6. verifier label,
7. retrieved token count,
8. downstream success or failure.

The target should be a structured action:

```json
{
  "family": "storyworld_play_diary",
  "lookup": "turn_history",
  "keys": ["scarlett_letter", "Hester", "MarketScaffold"],
  "top_k": 3,
  "compression": "summary_atoms",
  "decision": "retrieve_then_answer"
}
```

The most important design choice is pointer output. Natural-language router output wastes tokens and is harder to verify.

## Metrics

The paper should report retrieval and downstream metrics separately:

1. first useful hit rate,
2. MCP calls per task,
3. tokens loaded per task,
4. verifier rejection precision on near misses,
5. solved-task latency,
6. answer or decision quality,
7. quality per 1k retrieved tokens,
8. catastrophic miss rate.

The main scaling metric should be quality-adjusted success per token, not raw success alone.

## Interpretation

TRM-MCP is a compactification method because it turns context use into a learned routing and verification problem. If the TRM can reliably choose a small evidence bundle, the LLM no longer needs to read a giant context blob to act competently.

The storyworld diary result is a useful environment study because it shows how memory lookup can improve repeated-play performance and prevent negative policy overrides. The generic matrix is useful because it shows how the same row schema can apply outside storyworlds, across filesystem, GitHub, and database surfaces.

## Limitations

The generic MCP matrix is currently a curated row set, not a trained neural TRM evaluation. It supports schema and methodology claims, not learned performance claims.

The storyworld diary result is an environment-study result under deterministic/NAV/diary policies. It should not be described as a raw LLM benchmark unless a separate LLM-backed run is added.

The current data does not yet measure token savings against a stuffed-context baseline for all surfaces. That should be part of the next experiment campaign.

## Next Experiments

The next paper-grade experiment is to train a small router/verifier TRM on the generic matrix plus expanded negatives, then evaluate on held-out MCP families.

The second experiment is to build a storyworld retrieval-TRM from play-diary rows and test whether it improves repeated play under fixed token budgets.

The third experiment is a context-efficiency matrix: stuffed context, embedding retrieval, rules-only retrieval, TRM-MCP retrieval, and strong-LLM retrieval planner. The target metric is downstream quality per 1k input tokens.
