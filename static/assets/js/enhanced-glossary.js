export const init = () => {
  const jsRequired = document.querySelector(".js-required");
  jsRequired.style.display = "block";

  const input = document.getElementById("filter-input");
  input.addEventListener("keyup", updateResults);
};

const updateResults = () => {
  const input = document.getElementById("filter-input");
  const filter = input.value.toUpperCase();
  const termElements = document.querySelectorAll(".term");
  const termGroups = document.querySelectorAll(".term-group");

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
    }
  });
};
