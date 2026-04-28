# Synthetic Tool Router MeTTa/TRM Ablation

Local model: `Qwen2.5-3B-Instruct-Q4_K_M-GGUF-llama.cpp-CUDA`. The LLM proposes; MeTTa/TRM gates validate and repair schema calls.

| Arm | Cases | Reward Total | Avg Reward | Mean Seconds |
| --- | ---: | ---: | ---: | ---: |
| `with_metta_runtime` | 3 | 3.0000 | 1.0000 | 6.3793 |
| `with_metta_runtime_repair` | 3 | 3.0000 | 1.0000 | 6.3793 |
| `without_metta` | 3 | 0.0000 | 0.0000 | 22.8444 |

## Per-Case Rows

| Case | Arm | Reward | Judge Note | Output Excerpt |
| --- | --- | ---: | --- | --- |
| `weather_celsius` | `without_metta` | 0.0000 | WRONG_TOOL expected=weather.lookup got=weather_lookup | { "tool": "weather_lookup", "arguments": { "city": "Santiago", "country": "Chile", "unit": "Celsius" } } [end of text] |
| `weather_celsius` | `with_metta_runtime` | 1.0000 | EXACT_TOOL_CALL | {"tool": "weather.lookup", "arguments": {"location": "Santiago, Chile", "unit": "celsius"}} [end of text] |
| `weather_celsius` | `with_metta_runtime_repair` | 1.0000 | EXACT_TOOL_CALL | {"tool":"weather.lookup","arguments":{"location":"Santiago, Chile","unit":"celsius"}} |
| `calendar_review` | `without_metta` | 0.0000 | WRONG_TOOL expected=calendar.create_event got=schedule_meeting | {"tool": "schedule_meeting", "arguments": {"topic": "Metta TRM sync", "date": "2026-05-04", "participants": ["Ada", "Ben"], "summary": "D... |
| `calendar_review` | `with_metta_runtime` | 1.0000 | EXACT_TOOL_CALL | {"tool": "calendar.create_event", "arguments": {"attendees": ["Ada", "Ben"], "date": "2026-05-04", "title": "Metta TRM sync"}} [end of text] |
| `calendar_review` | `with_metta_runtime_repair` | 1.0000 | EXACT_TOOL_CALL | {"tool":"calendar.create_event","arguments":{"attendees":["Ada","Ben"],"date":"2026-05-04","title":"Metta TRM sync"}} |
| `repo_search` | `without_metta` | 0.0000 | WRONG_TOOL expected=repo.search got=git_search | { "tool": "git_search", "arguments": { "repository": "github.com/user/repo", "phrase": "sentence lengths not strictly increasing", "limit... |
| `repo_search` | `with_metta_runtime` | 1.0000 | EXACT_TOOL_CALL | {"tool": "repo.search", "arguments": {"max_results": 5, "query": "sentence lengths not strictly increasing"}} [end of text] |
| `repo_search` | `with_metta_runtime_repair` | 1.0000 | EXACT_TOOL_CALL | {"tool":"repo.search","arguments":{"max_results":5,"query":"sentence lengths not strictly increasing"}} |
