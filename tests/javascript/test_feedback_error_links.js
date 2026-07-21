import { beforeAll, beforeEach, expect, jest, test } from "@jest/globals";

jest.useFakeTimers();

const renderTemplate = ({ checked = false } = {}) => `
  <div id="feedback-announcement"></div>
  <div id="feedback-widget">
    <button data-feedback-announcement="You have selected Yes. There are new questions to answer.">Trigger announcement</button>
    <div class="govuk-error-summary">
      <div class="govuk-error-summary__body">
        <a href="#id_what_went_well" data-scroll-target="what-went-well-container">Tell us what went well to continue</a>
      </div>
    </div>
    <input id="id_something_else" name="something_else" type="checkbox" ${checked ? "checked" : ""}>
    <div id="what-went-well-container"></div>
    <div id="what-went-wrong-container"></div>
    <div id="some-other-issue-container"></div>
  </div>
`;

describe("feedback error summary links", () => {
  beforeAll(() => {
    jest.isolateModules(() => {
      require("../../static/assets/js/feedback-announcement.js");
    });
  });

  beforeEach(() => {
    document.body.innerHTML = renderTemplate();

    const target = document.getElementById("what-went-well-container");
    target.scrollIntoView = jest.fn();
    target.focus = jest.fn();
  });

  test("centers the linked feedback section instead of following the fragment jump", () => {
    const link = document.querySelector(".govuk-error-summary a");
    const clickEvent = new MouseEvent("click", { bubbles: true, cancelable: true });

    link.dispatchEvent(clickEvent);

    const target = document.getElementById("what-went-well-container");

    expect(clickEvent.defaultPrevented).toBe(true);
    expect(target.scrollIntoView).toHaveBeenCalledWith({ block: "center", inline: "nearest" });
    expect(target.focus).toHaveBeenCalledWith({ preventScroll: true });
    expect(target).toHaveAttribute("tabindex", "-1");
  });

  test("syncs conditional feedback sections on load and checkbox changes", () => {
    document.body.innerHTML = renderTemplate();

    const checkbox = document.getElementById("id_something_else");
    const whatWentWell = document.getElementById("what-went-well-container");
    const whatWentWrong = document.getElementById("what-went-wrong-container");
    const someOtherIssue = document.getElementById("some-other-issue-container");

    document.dispatchEvent(new Event("DOMContentLoaded"));

    expect(whatWentWell).toHaveClass("govuk-!-display-none");
    expect(whatWentWrong).toHaveClass("govuk-!-display-none");
    expect(someOtherIssue).toHaveClass("govuk-!-display-none");

    checkbox.checked = true;
    checkbox.dispatchEvent(new Event("change", { bubbles: true }));

    expect(whatWentWell).not.toHaveClass("govuk-!-display-none");
    expect(whatWentWrong).not.toHaveClass("govuk-!-display-none");
    expect(someOtherIssue).not.toHaveClass("govuk-!-display-none");

    checkbox.checked = false;
    checkbox.dispatchEvent(new Event("change", { bubbles: true }));

    expect(whatWentWell).toHaveClass("govuk-!-display-none");
    expect(whatWentWrong).toHaveClass("govuk-!-display-none");
    expect(someOtherIssue).toHaveClass("govuk-!-display-none");
  });

  test("announces swapped feedback content and reapplies visible state after htmx swaps", () => {
    document.body.innerHTML = renderTemplate({ checked: true });

    const trigger = document.querySelector("[data-feedback-announcement]");
    const announcement = document.getElementById("feedback-announcement");
    const target = document.getElementById("what-went-well-container");

    target.classList.add("govuk-!-display-none");
    trigger.dispatchEvent(new MouseEvent("click", { bubbles: true }));

    const swapEvent = new CustomEvent("htmx:afterSwap", {
      bubbles: true,
      detail: { target: document.getElementById("feedback-widget") },
    });

    document.body.dispatchEvent(swapEvent);

    expect(announcement.textContent).toBe("");

    jest.runAllTimers();

    expect(announcement.textContent).toBe("You have selected Yes. There are new questions to answer.");
    expect(target).not.toHaveClass("govuk-!-display-none");
  });
});
