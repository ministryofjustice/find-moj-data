export const init = () => {
  const jsRequired = document.querySelector(".js-required");
  jsRequired.style.display = "block";

  const input = document.getElementById("filter-input");
  input.addEventListener("input", debounce(updateResults, 200));

  document.querySelectorAll("[data-action='clear-filter']").forEach(el => {
    el.addEventListener("click", clearFilter);
    return true;
  })
};

const clearFilter = () => {
  const input = document.getElementById("filter-input");
  input.value = "";
  updateResults();
}

const updateResults = () => {
  const input = document.getElementById("filter-input");
  const filter = input.value.toUpperCase();
  const termElements = document.querySelectorAll(".term");
  const termGroups = document.querySelectorAll(".term-group");
  const noResultsPanel = document.getElementById("no-results-panel")

  // Loop through all terms, and hide those who don't match the search query
  termElements.forEach((el) => {
    if (
      filter == "" ||
      el.dataset.term.startsWith(filter) ||
      el.dataset.term.includes(" " + filter)
    ) {
      el.classList.remove("govuk-!-display-none");
    } else {
      el.classList.add("govuk-!-display-none");
    }
  });

  let numberOfVisibleTermGroups = 0;

  // Loop through all term groups, and hide those without visible terms
  termGroups.forEach((el) => {
    const terms = Array.from(el.querySelectorAll(".term"));
    const isEmpty =
      terms.length === 0 ||
    terms.every((term) => term.classList.contains("govuk-!-display-none"));

    if (isEmpty) {
      el.classList.add("govuk-!-display-none");
    } else {
      el.classList.remove("govuk-!-display-none");
      numberOfVisibleTermGroups += 1;
    }
  });

  if(numberOfVisibleTermGroups > 0) {
    noResultsPanel.classList.add("govuk-!-display-none");
  } else {
    noResultsPanel.classList.remove("govuk-!-display-none");
  }
};

const debounce = (callback, wait) => {
  let timeoutId = null;

  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      callback(...args);
    }, wait);
  };
}
