import subprocess


def check_for_accessibility_issues(url, chromedriver_path=None):
    command = ["npx", "@axe-core/cli"]

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
