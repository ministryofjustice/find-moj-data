let feedbackAnnouncement = "";

function getSomethingElseCheckbox() {
  return document.querySelector('input[name="something_else"]');
}

function getWhatWentWellContainer() {
  return document.getElementById("what-went-well-container");
}

function getWhatWentWrongContainer() {
  return document.getElementById("what-went-wrong-container");
}

function toggleWhatWentWell() {
  const checkbox = getSomethingElseCheckbox();
  const container = getWhatWentWellContainer();

  if (!checkbox || !container) {
    return;
  }

  container.classList.toggle("govuk-!-display-none", !checkbox.checked);

}

function toggleWhatWentWrong() {
  const checkbox = getSomethingElseCheckbox();
  const container = getWhatWentWrongContainer();

  if (!checkbox || !container) {
    return;
  }

  container.classList.toggle("govuk-!-display-none", !checkbox.checked);

}

document.body.addEventListener("click", function (event) {
  const button = event.target.closest("[data-feedback-announcement]");
  if (!button) {
    return;
  }
  feedbackAnnouncement = button.dataset.feedbackAnnouncement;
});

document.body.addEventListener("change", function (event) {
  if (event.target && event.target.matches('input[name="something_else"]')) {
    toggleWhatWentWell();
    toggleWhatWentWrong();
  }
});

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
});

document.addEventListener("DOMContentLoaded", function () {
  toggleWhatWentWell();
  toggleWhatWentWrong();
});
