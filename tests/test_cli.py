from io import StringIO
from unittest.mock import patch

from click.testing import CliRunner

from diffsay.cli import main
from diffsay.diff import Diff
from diffsay.spinner import spinner


def test_resolve_bare_name() -> None:
    assert (
        Diff.resolve_model_id("Qwen2.5-Coder-1.5B-Instruct-4bit")
        == "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit"
    )


def test_resolve_full_huggingface_id() -> None:
    assert (
        Diff.resolve_model_id("mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit")
        == "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit"
    )


def test_resolve_other_org() -> None:
    assert Diff.resolve_model_id("other-org/custom-model") == "other-org/custom-model"


def test_resolve_local_path(tmp_path) -> None:
    model_dir = tmp_path / "local-model"
    model_dir.mkdir()
    assert Diff.resolve_model_id(str(model_dir)) == str(model_dir)


def test_clean_message_strips_fences_and_end_token() -> None:
    raw = "```text\nfeat(parser): strip fences\n```\n<|im_end|> leftover"
    assert Diff.clean_message(raw) == "feat(parser): strip fences"


def test_staged_diff_decodes_git_output() -> None:
    with patch("diffsay.diff.subprocess.check_output", return_value=b"diff --git a/x b/x\n"):
        assert Diff().staged() == "diff --git a/x b/x"


def test_main_exits_when_nothing_is_staged() -> None:
    runner = CliRunner()
    with patch.object(Diff, "staged", return_value=""):
        result = runner.invoke(main)
    assert result.exit_code == 1
    assert "No staged changes" in f"{result.output}{result.exception}"


def test_prepare_keeps_small_diffs() -> None:
    diff = "diff --git a/cli.py b/cli.py\n+print('ok')\n"
    worker = Diff()
    prepared = worker.prepare(diff)
    assert prepared == diff
    assert worker.truncated is False


def test_prepare_caps_large_hunks() -> None:
    source = "diff --git a/src/app.py b/src/app.py\n" + ("+" + "a" * 80 + "\n") * 20
    lockfile = "diff --git a/uv.lock b/uv.lock\n+lock-content\n"
    worker = Diff(max_hunk_chars=200)
    prepared = worker.prepare(source + lockfile)
    assert worker.truncated is True
    assert "[truncated]" in prepared
    assert "uv.lock" in prepared
    assert "content omitted" in prepared
    assert "+lock-content" not in prepared


def test_prepare_reports_lockfile_without_content() -> None:
    source = "diff --git a/src/app.py b/src/app.py\n+source-change\n"
    lockfile = "diff --git a/uv.lock b/uv.lock\n" + ("+lock" * 50 + "\n")
    worker = Diff()
    prepared = worker.prepare(source + lockfile)
    assert worker.truncated is False
    assert "+source-change" in prepared
    assert "uv.lock" in prepared
    assert "content omitted" in prepared
    assert "+lock" not in prepared


def test_prepare_reports_minified_assets_without_content() -> None:
    source = "diff --git a/src/app.py b/src/app.py\n+source-change\n"
    min_js = "diff --git a/dist/app.min.js b/dist/app.min.js\n+minified-bundle\n"
    source_map = "diff --git a/dist/app.js.map b/dist/app.js.map\n+map-data\n"
    worker = Diff()
    prepared = worker.prepare(source + min_js + source_map)
    assert worker.truncated is False
    assert "+source-change" in prepared
    assert "dist/app.min.js" in prepared
    assert "dist/app.js.map" in prepared
    assert "content omitted" in prepared
    assert "+minified-bundle" not in prepared
    assert "+map-data" not in prepared


def test_main_warns_when_diff_is_truncated() -> None:
    runner = CliRunner()
    huge = "diff --git a/a.py b/a.py\n" + ("+x" * 100 + "\n") * 300
    with (
        patch.object(Diff, "staged", return_value=huge),
        patch.object(Diff, "say", return_value="feat(a): update"),
    ):
        result = runner.invoke(main)
    chunks = [result.output]
    try:
        chunks.append(result.stderr)
    except ValueError:
        pass
    assert result.exit_code == 0
    assert "feat(a): update" in result.output
    assert "truncated" in "".join(chunks).lower()


def test_spinner_is_silent_without_tty(capsys) -> None:
    with spinner("working"):
        pass
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_spinner_writes_immediately_when_tty() -> None:
    fake = StringIO()
    fake.isatty = lambda: True  # type: ignore[method-assign]
    with patch("diffsay.spinner.sys.stderr", fake):
        with spinner("working"):
            text = fake.getvalue()
    assert "working" in text
    assert "\033[2K" in fake.getvalue()
