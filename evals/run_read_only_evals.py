import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CASES_FILE = (
    PROJECT_ROOT
    / "evals"
    / "read_only_cases.json"
)

ARTIFACTS_DIR = (
    PROJECT_ROOT
    / "evals"
    / "artifacts"
)

ARTIFACTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def load_cases():
    with open(
        CASES_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def run_codex(
    prompt: str,
):
    command = [
        "codex",
        "exec",
        "--json",
        prompt,
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        shell=True,
    )

    return result

def tool_was_used(
    raw_output: str,
    tool_name: str,
) -> bool:
    """
    Codex JSONL contains tool information in its event
    stream. For this lightweight portfolio evaluation,
    confirm the expected MCP tool name appears in the
    structured trace.
    """

    return tool_name in raw_output


def main():

    cases = load_cases()

    passed = 0

    print()
    print("=" * 65)
    print("AI Operations & Inventory - Agent Evaluation")
    print("=" * 65)
    print()

    for case in cases:

        print(
            f"{case['id']} - "
            f"{case['name']}"
        )

        result = run_codex(
            case["prompt"]
        )

        artifact_file = (
            ARTIFACTS_DIR
            / f"{case['id']}.jsonl"
        )

        artifact_file.write_text(
            result.stdout,
            encoding="utf-8",
        )

        expected_tools = (
            case["expected_tools"]
        )

        missing_tools = [
            tool
            for tool in expected_tools
            if not tool_was_used(
                result.stdout,
                tool,
            )
        ]

        process_ok = (
            result.returncode == 0
        )

        case_passed = (
            process_ok
            and not missing_tools
        )

        if case_passed:

            print("PASS")

            passed += 1

        else:

            print("FAIL")

            if not process_ok:

                print(
                    "  Codex process "
                    "returned an error."
                )

                print(
                    result.stderr[:500]
                )

            if missing_tools:

                print(
                    "  Missing expected "
                    f"tools: {missing_tools}"
                )

        print()

    total = len(cases)

    print("=" * 65)

    print(
        f"Result: {passed}/{total} "
        "evaluation cases passed"
    )

    print("=" * 65)


if __name__ == "__main__":
    main()