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

  // Loop through all terms, and hide those who don't match the search query
  termElements.forEach((el) => {
    if (filter == "" || el.dataset.term.startsWith(filter)) {
      el.classList.remove("govuk-!-display-none");
    } else {
      el.classList.add("govuk-!-display-none");
    }
  });
};
