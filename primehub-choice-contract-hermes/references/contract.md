# Primehub Choice Contract

Use this skill on tasks where the answer space is small but the output wrapper is strict.

Common contracts:

- `Final Answer: X`
- `\boxed{X}`
- `True` or `False`
- a single choice letter such as `A`

Failure modes this skill targets:

- correct latent answer, wrong wrapper
- correct wrapper family, wrong literal token
- overlong answer instead of one-line exact output

Preferred repair order:

1. recover semantic answer token
2. detect required wrapper from the prompt
3. emit the minimal exact wrapper
4. verify legality before final output
