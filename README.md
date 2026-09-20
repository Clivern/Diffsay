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
diffsay -m Qwen2.5-Coder-1.5B-Instruct-4bit
```

## Develop

```bash
uv sync
uv run ruff check src tests
uv run pytest
```
