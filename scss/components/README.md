# Custom components for Find MOJ Data

## Search component

This enhances a [GOV.UK text input](https://design-system.service.gov.uk/components/text-input/) to act as a search input.

It's intended for use as a service-wide search or as a way of filtering long manuals or lists.

### Expected behaviours

- Clearable via the "X" button or pressing escape
- Focusable, with a focus outline
- Highlights the button on hover

### Usage

The search box should:

- be used inside a form or other element with `role="search"`, to indicate it as a [search landmark](https://www.w3.org/WAI/ARIA/apg/practices/landmark-regions/).
- have a visually hidden label to identify the search functionality

#### With no search icon

This variant should be used only for search-as-you-type behaviour that does not require submitting a form.

See `enhanced-glossary.js`.

```html
<div class="app-search govuk-form-group">
  <label for="filter-input" class="govuk-label">Filter this page</label>
  <input
    id="filter-input"
    class="govuk-input"
    type="search"
    placeholder="Filter this page" />
</div>
```

#### With an integrated search button

This variant submits the form when the button is pressed or the user presses enter.

```html
<form action="" method="get" role="search" class="govuk-!-margin-bottom-4">
  <div class="app-search app-search--compact govuk-form-group">
    <label
      for="search-input"
      class="govuk-label govuk-visually-hidden-focusable"
      >Search query</label
    >
    <input class="search-input govuk-input" type="search" />
    <button id="search-input" type="submit">
      <svg
        aria-hidden="true"
        focusable="false"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 36 36"
        width="40"
        height="40">
        <path
          d="M25.7 24.8L21.9 21c.7-1 1.1-2.2 1.1-3.5 0-3.6-2.9-6.5-6.5-6.5S10 13.9 10 17.5s2.9 6.5 6.5 6.5c1.6 0 3-.6 4.1-1.5l3.7 3.7 1.4-1.4zM12 17.5c0-2.5 2-4.5 4.5-4.5s4.5 2 4.5 4.5-2 4.5-4.5 4.5-4.5-2-4.5-4.5z"
          fill="currentColor"></path>
      </svg>
      <label class="govuk-label govuk-visually-hidden-focusable">Search</label>
    </button>
  </div>
</form>
```

## Blue background variant

Use this variant on a blue background to change the button colour to black.

```html
<form action="" method="get" role="search" class="govuk-!-margin-bottom-4">
  <label for="search-input" class="govuk-label govuk-label--m"
    >Search query</label
  >
  <div
    class="app-search app-search--compact app-search--on-govuk-blue govuk-form-group">
    <input id="search-input" class="search-input govuk-input" type="search" />
    <button type="submit">
      <svg
        aria-hidden="true"
        focusable="false"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 36 36"
        width="40"
        height="40">
        <path
          d="M25.7 24.8L21.9 21c.7-1 1.1-2.2 1.1-3.5 0-3.6-2.9-6.5-6.5-6.5S10 13.9 10 17.5s2.9 6.5 6.5 6.5c1.6 0 3-.6 4.1-1.5l3.7 3.7 1.4-1.4zM12 17.5c0-2.5 2-4.5 4.5-4.5s4.5 2 4.5 4.5-2 4.5-4.5 4.5-4.5-2-4.5-4.5z"
          fill="currentColor"></path>
      </svg>
      <label class="govuk-label govuk-visually-hidden-focusable">Search</label>
    </button>
  </div>
</form>
```

### Similar components elsewhere

- [GOV.UK publishing components search](https://components.publishing.service.gov.uk/component-guide/search)
- [Explore education statistics search](https://github.com/dfe-analytical-services/explore-education-statistics/blob/8a9aa729636eade2808895ad71a56bcb984d3c53/src/explore-education-statistics-common/src/components/form/FormSearchBar.module.scss)
- [MOJ search](https://design-patterns.service.justice.gov.uk/components/search/) and [icon](https://github.com/dfe-analytical-services/explore-education-statistics/blob/8a9aa729636eade2808895ad71a56bcb984d3c53/src/explore-education-statistics-common/src/components/SearchIcon.tsx#L4)
- [MOJ filter](https://design-patterns.service.justice.gov.uk/components/filter/)

## Masthead component

The masthead is an extended header with search included.

### Usage

```html
<div class="app-masthead">
  <div class="govuk-width-container app-width-container">
    <div class="govuk-grid-row">
      <div class="govuk-grid-column-two-thirds">
        <h1 class="govuk-heading-xl app-masthead__title">Find MOJ Data</h1>
        <h2 class="govuk-heading-m app-masthead__title">
          Search metadata catalogue
        </h2>
      </div>
    </div>
  </div>
</div>
```

### Similar components elsewhere

- [GOV.UK Design system documentation](https://github.com/alphagov/govuk-design-system/blob/b3223714d8f2e9564b7e9d2ca703a3f902bf1ce8/src/stylesheets/components/_masthead.scss)
