import { init } from "enhanced-glossary";
import { expect, test } from "@jest/globals";

const simplifiedPage = `
<div class="js-required">
<input class="govuk-input" id="filter-input" placeholder="Filter this page">
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

beforeEach(() => {
  document.body.innerHTML = simplifiedPage;

  filter = document.getElementById("filter-input");
  apple = document.getElementById("apple");
  banana = document.getElementById("banana");
  things = document.getElementById("things");

  init();
});

test("everything is shown when the filter is empty", () => {
  filter.value = "";
  filter.dispatchEvent(new Event("keyup"));

  expect(things).not.toHaveClass("govuk-!-display-none");
  expect(apple).not.toHaveClass("govuk-!-display-none");
  expect(banana).not.toHaveClass("govuk-!-display-none");
});

test("filtering to a term by its prefix", () => {
  filter.value = "ap";
  filter.dispatchEvent(new Event("keyup"));

  expect(things).not.toHaveClass("govuk-!-display-none");
  expect(apple).not.toHaveClass("govuk-!-display-none");
  expect(banana).toHaveClass("govuk-!-display-none");
});

test("filtering out all terms within a group", () => {
  filter.value = "carrot";
  filter.dispatchEvent(new Event("keyup"));

  expect(things).toHaveClass("govuk-!-display-none");
  expect(apple).toHaveClass("govuk-!-display-none");
  expect(banana).toHaveClass("govuk-!-display-none");
});
