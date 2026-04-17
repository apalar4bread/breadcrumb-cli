import subprocess
import time
from typing import Optional
from breadcrumb.session import Session, Step


def replay_session(
    session: Session,
    dry_run: bool = False,
    delay: float = 0.5,
    stop_on_error: bool = True,
) -> list[dict]:
    """Replay all steps in a session, returning results."""
    results = []

    for i, step in enumerate(session.steps):
        result = replay_step(step, dry_run=dry_run)
        results.append(result)

        if result["returncode"] != 0 and stop_on_error:
            print(f"Step {i + 1} failed (exit {result['returncode']}). Stopping.")
            break

        if delay > 0 and not dry_run:
            time.sleep(delay)

    return results


def replay_step(step: Step, dry_run: bool = False) -> dict:
    """Run a single step command, return result dict."""
    print(f"  $ {step.command}")

    if dry_run:
        return {"command": step.command, "returncode": 0, "stdout": "", "stderr": "", "dry_run": True}

    try:
        proc = subprocess.run(
            step.command,
            shell=True,
            capture_output=True,
            text=True,
        )
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="")

        return {
            "command": step.command,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "dry_run": False,
        }
    except Exception as e:
        return {
            "command": step.command,
            "returncode": 1,
            "stdout": "",
            "stderr": str(e),
            "dry_run": False,
        }
