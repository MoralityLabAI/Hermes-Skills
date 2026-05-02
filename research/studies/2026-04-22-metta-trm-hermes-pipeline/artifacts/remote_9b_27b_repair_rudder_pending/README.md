# Remote 9B/27B Repair Rudder Benchmark Pending

Date: 2026-05-02

Purpose: fill the Skills paper data-campaign rows for matched 9B and 27B
repair-training rudder benchmarks over the same non-train Pure-TRM split used by
the local 3B run.

Runner:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py
```

Endpoint probe result on 2026-05-02:

```json
{
  "9b": {
    "url": "http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1/models",
    "ok": false,
    "error": "timed out"
  },
  "27b": {
    "url": "http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1/models",
    "ok": false,
    "error": "timed out"
  }
}
```

SSH also timed out for both `snacksack` and `snacksack-patrick`, so no remote job
was launched.

## Safe Launch

Probe only:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py --probe-only --endpoint-probe-timeout 8
```

Small smoke, one case per model:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py --max-cases 1 --request-timeout 180 --max-runtime-minutes 20
```

Full matched benchmark for paper table:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py --max-cases 0 --request-timeout 240 --max-runtime-minutes 240
```

Highest-signal scale question only, raw versus training context:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py --max-cases 0 --arm raw_3b_rudder --arm repair_training_rudder --request-timeout 240 --max-runtime-minutes 240
```

## Output Shape

Each model run writes:

- `remote_repair_training_rudder.rows.jsonl`
- `remote_repair_training_rudder.results.json`
- `remote_repair_training_rudder.results.md`

The summary schema mirrors the local 3B benchmark and reports target-action
accuracy, repair-action accuracy, joint accuracy, JSON parse rate, and split
coverage by arm.
