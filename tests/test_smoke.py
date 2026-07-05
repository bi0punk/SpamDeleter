from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repo_has_readme():
    assert (REPO_ROOT / "README.md").exists()


def test_repo_has_gitignore():
    assert (REPO_ROOT / ".gitignore").exists()


def test_env_example():
    assert (REPO_ROOT / ".env.example").exists()


def test_cli_import():
    import importlib
    importlib.import_module("spam_deleter")
