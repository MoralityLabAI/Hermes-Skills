# Row Format

The TRM row builder should preserve these fields:

- source family
- row identifier
- skill name
- input prompt or observation
- exact-positive label
- negative label
- route label
- target label
- support signature or support phrase
- response mode / reasoning mode
- failure type and recovery labels
- evaluation outcome

## Row principles

- Keep one row per example.
- Keep the labels explicit.
- Keep the route decision auditable.
- Keep family-level summary counts with the dataset.

## Expected use

- exact positives feed retrieval-style training
- all rows feed critic-style training
- route labels feed router and correction training

## Merge rule

Use a family floor so weak batches do not wash out strong logic or math
corpora.
