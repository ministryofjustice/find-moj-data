import subprocess


def check_for_accessibility_issues(url, chromedriver_path=None, axe_version="latest"):
    command = ["npx", f"@axe-core/cli@{axe_version}"]

    if chromedriver_path:
        command.extend(["--chromedriver-path", chromedriver_path])

    command.extend(
        [
            "-q",
            url,
        ]
    )

    output = subprocess.run(command, capture_output=True, text=True)
    assert output.returncode == 0, output.stdout
