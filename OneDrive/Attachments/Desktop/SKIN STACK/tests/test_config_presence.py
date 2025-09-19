from pathlib import Path


def test_required_configs_exist():
    repo = Path(__file__).resolve().parents[1]
    assert (repo / "pyproject.toml").exists()
    assert (repo / ".pre-commit-config.yaml").exists()
    assert (repo / ".sqlfluff").exists()
    assert (repo / ".github" / "workflows" / "ci.yml").exists()


