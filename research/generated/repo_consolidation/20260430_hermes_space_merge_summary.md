# Hermes directory consolidation

Date: 2026-04-30

Source: `C:\projects\Hermes Skills`
Target: `C:\projects\Hermes-Skills\Hermes Skills`
Policy: copy missing files and overwrite only when source `LastWriteTimeUtc` is newer; preserve target when target is newer.

Final verification: `0` source files remain missing from the target; `0` same-path source files are newer than the target.

Long-path note: `11` deeply nested artifact files required a second pass with Windows `\\?\` long-path prefixes and were copied successfully.

## Copied
- copied_missing: 9288

## Skipped
- kept_target_newer_size_diff: 165
- kept_target_same_or_newer: 691

Detailed manifests:
- `20260430_hermes_space_merge_copied.jsonl`
- `20260430_hermes_space_merge_skipped.jsonl`
