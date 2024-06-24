# Search component

This enhances a [GOV.UK text input](https://design-system.service.gov.uk/components/text-input/) to act as a search input.

It's intended for use as a service-wide search or as a way of filtering long manuals or lists.

## Similar components elsewhere

- [GOV.UK publishing components search](https://components.publishing.service.gov.uk/component-guide/search)
- [Explore education statistics search](https://github.com/dfe-analytical-services/explore-education-statistics/blob/8a9aa729636eade2808895ad71a56bcb984d3c53/src/explore-education-statistics-common/src/components/form/FormSearchBar.module.scss)
- [MOJ search](https://design-patterns.service.justice.gov.uk/components/search/) and [icon](https://github.com/dfe-analytical-services/explore-education-statistics/blob/8a9aa729636eade2808895ad71a56bcb984d3c53/src/explore-education-statistics-common/src/components/SearchIcon.tsx#L4)
- [MOJ filter](https://design-patterns.service.justice.gov.uk/components/filter/)

## Usage

### With no search icon

```html
<div class="fmj-search govuk-form-group">
  <label for="filter-input" class="govuk-label">Filter this page</label>
  <input class="govuk-input" type="search" />
</div>
```

### With an integrated search button

```html
<form action="" method="get" role="search" class="govuk-!-margin-bottom-4">
  <div class="fmj-search fmj-search--compact govuk-form-group">
    <label
      for="search-input"
      class="govuk-label govuk-visually-hidden-focusable"
      >Search query</label
    >
    <input class="search-input govuk-input" type="search" />
    <button type="submit">
      <svg
        aria-hidden="true"
        focusable="false"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 36 36"
        width="40"
        height="40"
      >
        <path
          d="M25.7 24.8L21.9 21c.7-1 1.1-2.2 1.1-3.5 0-3.6-2.9-6.5-6.5-6.5S10 13.9 10 17.5s2.9 6.5 6.5 6.5c1.6 0 3-.6 4.1-1.5l3.7 3.7 1.4-1.4zM12 17.5c0-2.5 2-4.5 4.5-4.5s4.5 2 4.5 4.5-2 4.5-4.5 4.5-4.5-2-4.5-4.5z"
          fill="currentColor"
        ></path>
      </svg>
      <label
        for="search-button"
        class="govuk-label govuk-visually-hidden-focusable"
        >Search</label
      >
    </button>
  </div>
</form>
```
