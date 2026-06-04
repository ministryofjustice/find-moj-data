let feedbackAnnouncement = '';

document.body.addEventListener('click', function (event) {
  const button = event.target.closest('[data-feedback-announcement]');

  if (!button) {
    return;
  }

  feedbackAnnouncement = button.dataset.feedbackAnnouncement;
});

document.body.addEventListener('htmx:afterSwap', function (event) {
  if (!event.detail.target || event.detail.target.id !== 'feedback-widget') {
    return;
  }

  const announcement = document.getElementById('feedback-announcement');

  if (!announcement) {
    return;
  }

  announcement.textContent = '';

  window.setTimeout(function () {
    announcement.textContent = feedbackAnnouncement || 'There are new questions to answer.';
  }, 50);
});
