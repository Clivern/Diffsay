from __future__ import annotations

import os
import re
import subprocess

from diffsay.const import (
    DEFAULT_MODEL,
    DEFAULT_MODEL_ORG,
    DIFF_FILE_RE,
    DIFF_SPLIT_RE,
    HF_ID_SEPARATOR,
    LOW_PRIORITY_FILES,
    LOW_PRIORITY_SUFFIXES,
    MAX_HUNK_CHARS,
)


class Diff:
    DEFAULT_MODEL_ORG = DEFAULT_MODEL_ORG
    DEFAULT_MODEL = DEFAULT_MODEL

    def __init__(
        self,
        model: str | None = None,
        *,
        max_hunk_chars: int = MAX_HUNK_CHARS,
    ) -> None:
        self.model = self.resolve_model_id(model or self.DEFAULT_MODEL)
        self.max_hunk_chars = max_hunk_chars
        self.truncated = False

    @staticmethod
    def resolve_model_id(model_id: str) -> str:
        """Accept a local path, a full Hugging Face id, or a bare mlx-community name."""
        if os.path.isdir(model_id) or HF_ID_SEPARATOR in model_id:
            return model_id
        return f"{Diff.DEFAULT_MODEL_ORG}/{model_id}"

    def staged(self) -> str:
        diff = subprocess.check_output(["git", "diff", "--staged"]).decode(
            "utf-8", errors="replace"
        )
        return diff.strip()

    @staticmethod
    def clean_message(raw_text: str) -> str:
        clean = re.sub(r"```[a-zA-Z]*", "", raw_text)
        clean = clean.replace("```", "")
        clean = clean.split("<|im_end|>")[0]
        return clean.strip()

    def prepare(self, diff_text: str) -> str:
        omitted: list[str] = []
        parts: list[str] = []
        self.truncated = False

        for hunk in (hunk for hunk in DIFF_SPLIT_RE.split(diff_text) if hunk):
            path = self._hunk_path(hunk)
            if path and self._is_low_priority(path):
                omitted.append(path)
                continue
            if len(hunk) > self.max_hunk_chars:
                hunk = hunk[: self.max_hunk_chars].rstrip() + "\n[truncated]\n"
                self.truncated = True
            parts.append(hunk)

        text = "".join(parts)
        if omitted:
            text = self._omitted_notice(omitted) + text
        return text

    def say(self, diff_text: str) -> str:
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        os.environ["TQDM_DISABLE"] = "1"

        from mlx_lm import generate, load

        diff_text = self.prepare(diff_text)
        model, tokenizer = load(self.model)
        prompt = (
            "Write one Conventional Commit subject for the change below.\n"
            "Use type(scope): description or type: description.\n"
            "Types: feat, fix, docs, test, ci, refactor, chore.\n"
            "feat = new behavior or a new project. fix = bug repair only.\n"
            "Summarize the whole change. Reply with the subject line only.\n\n"
            f"{diff_text}"
        )
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        raw_response = generate(
            model,
            tokenizer,
            prompt=formatted_prompt,
            max_tokens=60,
            verbose=False,
        )
        return self.clean_message(raw_response)

    @staticmethod
    def _hunk_path(hunk: str) -> str:
        match = DIFF_FILE_RE.search(hunk)
        return match.group(1) if match else ""

    @staticmethod
    def _is_low_priority(path: str) -> bool:
        name = path.rsplit("/", 1)[-1]
        return name in LOW_PRIORITY_FILES or path.endswith(LOW_PRIORITY_SUFFIXES)

    @staticmethod
    def _omitted_notice(paths: list[str]) -> str:
        listed = "\n".join(f"- {path}" for path in paths)
        return f"These files also changed (content omitted):\n{listed}\n\n"
