import { init, calculateCurrentTermGroup } from "enhanced-glossary";
import { expect, test, jest, beforeEach } from "@jest/globals";

jest.useFakeTimers();

const simplifiedPage = `
<div class="js-required">
<input type="search" class="govuk-input" id="filter-input" placeholder="Filter this page">
<div class="govuk-!-display-none" id="no-results-panel">
    <h2 class="govuk-heading-m">No terms found</h2>
    <p class="govuk-body">There are no terms in the glossary matching your search query.</p>
</div>
<div id="things" class="term-group">
  <h2>Things</h2>
  <p>Bla bla bla</p>
  <hr>

  <div id="apple" data-term="APPLE" class="term">
      <h3>Apple</h3>
      <p>Apples apples apples</p>
  </div>

  <div id="banana" data-term="BANANA" class="term">
      <h3>Banana</h3>
      <p>Banananaananaa</p>
  </div>
</div>
</div>
`;

let filter;
let apple;
let banana;
let things;
let noResultsPanel;

describe("filtering the glossary", () => {
  beforeEach(() => {
    document.body.innerHTML = simplifiedPage;

    filter = document.getElementById("filter-input");
    apple = document.getElementById("apple");
    banana = document.getElementById("banana");
    things = document.getElementById("things");
    noResultsPanel = document.getElementById("no-results-panel");

    init();
  });

  test("everything is shown when the filter is empty", () => {
    filter.value = "";
    filter.dispatchEvent(new Event("input"));
    jest.runAllTimers();

    expect(things).not.toHaveClass("govuk-!-display-none");
    expect(apple).not.toHaveClass("govuk-!-display-none");
    expect(banana).not.toHaveClass("govuk-!-display-none");
    expect(noResultsPanel).toHaveClass("govuk-!-display-none");
  });

  test("filtering to a term by its prefix", () => {
    filter.value = "ap";
    filter.dispatchEvent(new Event("input"));
    jest.runAllTimers();

    expect(things).not.toHaveClass("govuk-!-display-none");
    expect(apple).not.toHaveClass("govuk-!-display-none");
    expect(banana).toHaveClass("govuk-!-display-none");
    expect(noResultsPanel).toHaveClass("govuk-!-display-none");
  });

  test("filtering out all terms within a group", () => {
    filter.value = "carrot";
    filter.dispatchEvent(new Event("input"));
    jest.runAllTimers();

    expect(things).toHaveClass("govuk-!-display-none");
    expect(apple).toHaveClass("govuk-!-display-none");
    expect(banana).toHaveClass("govuk-!-display-none");
    expect(noResultsPanel).not.toHaveClass("govuk-!-display-none");
  });
});

describe('navigation highlights', () => {
  test("when nothing is visible, no section is highlighted", () => {
    const result = calculateCurrentTermGroup({
      window: {innerHeight: 300, scrollY: 0},
      documentHeight: 1000,
      visibleTermGroups: []
    });

    expect(result).toEqual(null);
  });

  test("at the top of the page, the first section is highlighted", () => {
    const result = calculateCurrentTermGroup({
      window: {innerHeight: 300, scrollY: 0},
      documentHeight: 1000,
      visibleTermGroups: [{top: 100, bottom: 200, name: "a"}, {top: 200, bottom: 300, name: "b"}, {top: 300, bottom: 400, name: "c"}]
    });

    expect(result).toEqual({top: 100, bottom: 200, name: "a"});
  });

  test("when you scroll to a new section, it is highlighted", () => {
    const result = calculateCurrentTermGroup({
      window: {innerHeight: 300, scrollY: 150},
      documentHeight: 1000,
      visibleTermGroups: [{top: -150, bottom: -50, name: "a"}, {top: 50, bottom: 150, name: "b"}, {top: 250, bottom: 350, name: "c"}]
    });

    expect(result).toEqual({top: 50, bottom: 150, name: "b"});
  });

  test("at the bottom of the page, the last section is highlighted", () => {
    const result = calculateCurrentTermGroup({
      window: {innerHeight: 300, scrollY: 700},
      documentHeight: 1000,
      visibleTermGroups: [{top: -700, bottom: -600, name: "a"}, {top: -600, bottom: -500, name: "b"}, {top: -400, bottom: -300, name: "c"}]
    });

    expect(result).toEqual({top: -400, bottom: -300, name: "c"});
  });
})
