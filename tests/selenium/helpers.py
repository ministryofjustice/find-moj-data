import subprocess


def check_for_accessibility_issues(url):
    command = ["npx", "@axe-core/cli", "-q", url]
    output = subprocess.run(command, capture_output=True, text=True)
    assert output.returncode == 0, output.stdout
