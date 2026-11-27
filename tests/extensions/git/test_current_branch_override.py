"""Regression coverage for explicit branch reuse in the git extension."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.extensions.git.test_git_extension import _run_pwsh
from tests.extensions.git.test_git_extension_python_parity import (
    _branch_state,
    _run_py,
    _setup_py_project,
)
from tests.parity_helpers import WINDOWS_POWERSHELL


# Exercise Windows PowerShell 5.1 when available, including on machines that
# also have PowerShell 7 installed.
POWERSHELL_EXE = WINDOWS_POWERSHELL or shutil.which("pwsh")


def _bash_environment(executable, extra=None):
    env = {**os.environ, **(extra or {})}
    env["PATH"] = str(Path(executable).parent) + os.pathsep + env.get("PATH", "")
    return env


def _find_bash():
    candidates = []
    git = shutil.which("git")
    if os.name == "nt" and git:
        for parent in Path(git).resolve().parents:
            candidates.extend([
                parent / "usr" / "bin" / "bash.exe",
                parent / "bin" / "bash.exe",
            ])
    on_path = shutil.which("bash")
    if on_path:
        candidates.append(Path(on_path))
    for candidate in candidates:
        if not candidate.is_file():
            continue
        executable = str(candidate.resolve())
        try:
            result = subprocess.run(
                [executable, "-c", "uname -s"], capture_output=True, text=True,
                timeout=5, env=_bash_environment(executable),
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        kernel = result.stdout.upper()
        if result.returncode == 0 and (
            os.name != "nt" or any(k in kernel for k in ("MSYS", "MINGW", "CYGWIN"))
        ):
            return executable
    return None


BASH_EXE = _find_bash()


@pytest.fixture(
    params=[
        "python",
        pytest.param(
            "bash",
            marks=pytest.mark.skipif(
                BASH_EXE is None, reason="working native Bash not available"
            ),
        ),
        pytest.param(
            "powershell",
            marks=pytest.mark.skipif(
                POWERSHELL_EXE is None, reason="PowerShell not available"
            ),
        ),
    ]
)
def branch_script(request, tmp_path):
    project = _setup_py_project(tmp_path / "project")

    def run(branch_name):
        env = {"GIT_BRANCH_NAME": branch_name}
        if request.param == "python":
            return _run_py(
                "create-new-feature-branch", project,
                "--json", "--short-name", "login", "Login page", env_extra=env,
            )
        if request.param == "bash":
            script = (
                project / ".specify" / "extensions" / "git" / "scripts"
                / "bash" / "create-new-feature-branch.sh"
            )
            return subprocess.run(
                [BASH_EXE, str(script), "--json", "--short-name", "login", "Login page"],
                cwd=project, capture_output=True, text=True,
                env=_bash_environment(BASH_EXE, env),
            )
        return _run_pwsh(
            "create-new-feature-branch.ps1", project,
            "-Json", "-ShortName", "login", "Login page",
            env_extra=env, exe=POWERSHELL_EXE,
        )

    return project, run


@pytest.mark.parametrize(
    "branch_name,feature_num",
    [
        ("feature/PROJ-42-login", "feature/PROJ-42-login"),
        ("fix/5003-current-branch", "5003"),
    ],
)
def test_explicit_current_branch_is_reused(branch_script, branch_name, feature_num):
    """An explicit current branch succeeds repeatedly without an allow flag."""
    project, run = branch_script
    subprocess.run(
        ["git", "checkout", "-q", "-b", branch_name], cwd=project, check=True,
    )
    before = _branch_state(project)

    for _ in range(2):
        result = run(branch_name)

        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout) == {
            "BRANCH_NAME": branch_name,
            "FEATURE_NUM": feature_num,
        }
        assert _branch_state(project) == before


def test_other_existing_branch_still_requires_allow_flag(branch_script):
    """An explicit different existing branch must fail without switching."""
    project, run = branch_script
    target = "feature/PROJ-42-login"
    subprocess.run(
        ["git", "checkout", "-q", "-b", "feature/current"], cwd=project, check=True,
    )
    subprocess.run(["git", "branch", target], cwd=project, check=True)
    before = _branch_state(project)

    result = run(target)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "already exists" in result.stderr
    assert result.stdout.strip() == ""
    assert _branch_state(project) == before
