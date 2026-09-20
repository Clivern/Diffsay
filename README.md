## Diffsay

Generate a Conventional commit message from the staged git diff, locally with MLX.

Requires Python 3.10+ and Apple silicon.

### Install

```bash
uv tool install diffsay
```

Or from this repo:

```bash
uv tool install .
```

### Usage

```bash
git add .
diffsay
```

Prints one Conventional Commit subject line on stdout.

Default model is `Qwen2.5-Coder-7B-Instruct-4bit`. Bare names resolve under `mlx-community/`.

```bash
diffsay -m Qwen2.5-Coder-14B-Instruct-4bit
```

Use a 7B+ instruct model. Sub-3B models (Gemma 1B, Qwen 1.5B) tend to invent tokens and ignore the “one line” rule.

| Model | RAM (4-bit) | Notes |
| --- | --- | --- |
| `Qwen2.5-Coder-7B-Instruct-4bit` | ~6–8 GB | Default |
| `Qwen2.5-Coder-14B-Instruct-4bit` | ~10–12 GB | Better whole-diff summaries |
| `Qwen2.5-Coder-32B-Instruct-4bit` | ~20+ GB | Needs 24+ GB unified memory |
| `Llama-3.1-8B-Instruct-4bit` | ~6–8 GB | US, follows instructions well |
| `Qwen3-8B-Instruct-4bit` | ~6–8 GB | Newer general model |
| `Qwen3-14B-Instruct-4bit` | ~10–12 GB | Stronger feat vs fix |


## Develop

```bash
uv sync
uv run ruff check src tests
uv run pytest
```
