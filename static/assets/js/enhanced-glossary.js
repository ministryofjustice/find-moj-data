export const init = () => {
  const jsRequired = document.querySelector(".js-required");
  jsRequired.style.display = "block";

  const input = document.getElementById("filter-input");
  input.addEventListener("input", debounce(updateResults, 200));

  document.querySelectorAll("[data-action='clear-filter']").forEach(el => {
    el.addEventListener("click", clearFilter);
    return true;
  });

  window.addEventListener("scroll", debounce(highlightCurrentTermGroup, 100));
  window.addEventListener("resize", debounce(highlightCurrentTermGroup, 100));
  highlightCurrentTermGroup();
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

  highlightCurrentTermGroup();
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

const highlightCurrentTermGroup = () => {
  const termGroups = Array.from(document.querySelectorAll("#glossary-content .term-group"));
  const visibleTermGroups = termGroups
    .filter(elem => !elem.classList.contains("govuk-!-display-none"))
    .map(termGroup => {
      const rect = termGroup.getBoundingClientRect();
      const name = termGroup.dataset.name;
      return {
        top: rect.top,
        bottom: rect.bottom,
        name: name
      }
    });

  let selectedTermGroup = calculateCurrentTermGroup({window, documentHeight: document.documentElement.offsetHeight, visibleTermGroups});

  document.querySelectorAll(".glossary-nav-link").forEach(link => {
    if(selectedTermGroup !== null && link.dataset.name == selectedTermGroup.name) {
      link.classList.add("govuk-!-font-weight-bold");
    } else {
      link.classList.remove("govuk-!-font-weight-bold");
    }
  })

}

export const calculateCurrentTermGroup = ({window, documentHeight, visibleTermGroups}) => {
  const closeEnough = 20;

  if(visibleTermGroups.length === 0) {
    // If none of the term groups are visible, do nothing.
    return null;
  } else if (Math.abs(window.innerHeight + window.scrollY - documentHeight) < closeEnough) {
    // If we are scrolled almost to the bottom of the page, select the last group, even if
    // the previous group is still on screen
    return visibleTermGroups[visibleTermGroups.length - 1];
  } else {
    // Pick the first section such that
    // 1. the top of the section is in view or above the top of the viewport
    // 2. AND the bottom 20px of the section is in view or below the bottom of the viewport
    for(const termGroup of visibleTermGroups) {
      if(
        termGroup.top <= window.innerHeight && termGroup.bottom > closeEnough
      ) {
        return termGroup;
      }
    }
  }

  return null;
};
