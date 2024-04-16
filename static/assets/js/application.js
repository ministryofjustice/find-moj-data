export const init = () => {
  const moreLessToggles = document.querySelectorAll(
    '[data-module="more-less-toggle"]'
  );
  moreLessToggles.forEach(initMoreOrLess);
};

const initMoreOrLess = (element) => {
  const button = element.querySelector(":scope > .govuk-button");
  const ellipsis = element.querySelector(":scope > .more-less-ellipsis");
  const remainder = element.querySelector(":scope > .more-less-remainder");
  let expanded = false;

  if (button === null || ellipsis === null || remainder == null) {
    console.error("Invalid more-or-less toggle");
    console.error(element);
    return;
  }

  const more = () => {
    ellipsis.style.display = "none";
    remainder.style.display = "inline";
    button.textContent = "Show less";
    button.style.display = "block";
  };

  const less = () => {
    ellipsis.style.display = "inline";
    remainder.style.display = "none";
    button.textContent = "Show more";
    button.style.display = "block";
  };

  button.addEventListener("click", () => {
    expanded = !expanded;

    if (expanded) {
      more();
    } else {
      less();
    }
  });

  less();
};
