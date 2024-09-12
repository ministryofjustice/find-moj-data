from datetime import datetime
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

phase_report_key = pytest.StashKey[dict[str, pytest.CollectReport]]()

TMP_DIR = (Path(__file__).parent.parent / "tmp").resolve()


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    rep = yield

    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep

    return rep


@pytest.fixture(autouse=True)
def screenshotter(request, selenium: RemoteWebDriver):
    yield

    testname = request.node.name
    report = request.node.stash[phase_report_key]

    if report["setup"].failed:
        # Nothing to screenshot
        pass

    elif ("call" not in report) or report["call"].failed:
        timestamp = datetime.now().strftime(r"%Y%m%d%H%M%S")
        TMP_DIR.mkdir(exist_ok=True)
        path = str(TMP_DIR / f"{timestamp}-{testname}-failed.png")
        total_height = selenium.execute_script(
            "return document.body.parentNode.scrollHeight"
        )
        selenium.set_window_size(1920, total_height)
        selenium.save_screenshot(path)
        print(f"Screenshot saved to {path}")
