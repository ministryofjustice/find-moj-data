let feedbackAnnouncement = "";

function getFeedbackWidget() {
  return document.getElementById("feedback-widget");
}

function getFeedbackErrorTarget(link) {
  if (!link) {
    return null;
  }

  const targetId = link.dataset.scrollTarget || link.getAttribute("href")?.slice(1);

  if (!targetId) {
    return null;
  }

  return document.getElementById(targetId);
}

function focusAndCenter(target) {
  if (!target) {
    return;
  }

  if (!target.hasAttribute("tabindex")) {
    target.setAttribute("tabindex", "-1");
  }

  target.scrollIntoView({block: "center", inline: "nearest"});

  if (typeof target.focus === "function") {
    target.focus({preventScroll: true});
  }
}

function getSomethingElseCheckbox() {
  return document.querySelector('input[name="something_else"]');
}

// Container for the Yes journey conditional textarea.
function getWhatWentWellContainer() {
  return document.getElementById("what-went-well-container");
}

// Container for the No journey conditional textarea.
function getWhatWentWrongContainer() {
  return document.getElementById("what-went-wrong-container");
}

// Container for the 'Some other issue' journey conditional textarea.
function getSomeOtherIssueContainer() {
  return document.getElementById("some-other-issue-container");
}

// Show/hide Yes conditional textarea based on "something_else" checkbox state.
function toggleWhatWentWell() {
  const checkbox = getSomethingElseCheckbox();
  const container = getWhatWentWellContainer();

  if (!checkbox || !container) {
    return;
  }

  container.classList.toggle("govuk-!-display-none", !checkbox.checked);

}

// Show/hide No conditional textarea based on "something_else" checkbox state.
function toggleWhatWentWrong() {
  const checkbox = getSomethingElseCheckbox();
  const container = getWhatWentWrongContainer();

  if (!checkbox || !container) {
    return;
  }

  container.classList.toggle("govuk-!-display-none", !checkbox.checked);

}

// Show/hide 'Some other issue' conditional textarea based on "something_else" checkbox state.
function toggleSomeOtherIssue() {
  const checkbox = getSomethingElseCheckbox();
  const container = getSomeOtherIssueContainer();

  if (!checkbox || !container) {
    return;
  }

  container.classList.toggle("govuk-!-display-none", !checkbox.checked);

}

// Capture the CTA's announcement message before HTMX swaps content.
document.body.addEventListener("click", function (event) {
  const button = event.target.closest("[data-feedback-announcement]");
  if (!button) {
    return;
  }
  feedbackAnnouncement = button.dataset.feedbackAnnouncement;
});

// React to checkbox changes in the live widget (event delegation for swapped markup).
document.body.addEventListener("change", function (event) {
  if (event.target && event.target.matches('input[name="something_else"]')) {
    toggleWhatWentWell();
    toggleWhatWentWrong();
    toggleSomeOtherIssue();
  }
});

document.body.addEventListener("click", function (event) {
  const link = event.target.closest("#feedback-widget .govuk-error-summary a");

  if (!link || !getFeedbackWidget()) {
    return;
  }

  const target = getFeedbackErrorTarget(link);

  if (!target) {
    return;
  }

  event.preventDefault();
  focusAndCenter(target);
});

// After HTMX updates #feedback-widget, re-announce and re-bind visual state.
document.body.addEventListener("htmx:afterSwap", function (event) {
  if (!event.detail.target || event.detail.target.id !== "feedback-widget") {
    return;
  }

  const announcement = document.getElementById("feedback-announcement");

  if (announcement) {
    announcement.textContent = "";
    window.setTimeout(function () {
      announcement.textContent = feedbackAnnouncement || "There are new questions to answer.";
    }, 50);
  }

  // Important: re-run after HTMX swaps in new form markup
  toggleWhatWentWell();
  toggleWhatWentWrong();
  toggleSomeOtherIssue();
});

// Initial page-load sync so server-rendered states match checkbox values.
document.addEventListener("DOMContentLoaded", function () {
  toggleWhatWentWell();
  toggleWhatWentWrong();
  toggleSomeOtherIssue();
});
