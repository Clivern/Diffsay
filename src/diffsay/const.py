import re

DEFAULT_MODEL_ORG = "mlx-community"
DEFAULT_MODEL = f"{DEFAULT_MODEL_ORG}/Qwen2.5-Coder-7B-Instruct-4bit"
MAX_HUNK_CHARS = 8_000

HF_ID_SEPARATOR = "/"
DIFF_SPLIT_RE = re.compile(r"(?=^diff --git )", re.MULTILINE)
DIFF_FILE_RE = re.compile(r"^diff --git a/.+ b/(.+)$", re.MULTILINE)
LOW_PRIORITY_FILES = {
    "Cargo.lock",
    "composer.lock",
    "go.sum",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}
LOW_PRIORITY_SUFFIXES = (".min.css", ".min.js", ".map")
