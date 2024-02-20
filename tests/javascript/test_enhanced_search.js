import { initDomainFilter } from "enhanced-search";
import { expect, test } from "@jest/globals";

const widget_html = `
    <fieldset class="govuk-fieldset">
        <legend class="govuk-fieldset__legend govuk-fieldset__legend--m">Domain</legend>
        <div class="govuk-form-group">
            <label class="govuk-label" for="domains-filter">
                Top-level
            </label>
            <select class="govuk-select" id="domains-filter" name="domains">
                <option value="*">All domains</option>
                <option value="a">Domain A</option>
                <option value="b">Domain B</option>
            </select>
        </div>
        <div class="govuk-form-group js-required">
            <label class="govuk-label" for="subdomains-filter">
                Subdomain
            </label>
            <select class="govuk-select" id="subdomains-filter" name="subdomains" disabled>
                <option value="*">All subdomains</option>
                <option value="a1" data-parent="a">Subdomain of A 1</option>
                <option value="a2" data-parent="a">Subdomain of A 2</option>
                <option value="b1" data-parent="b">Subdomain of B 1</option>
                <option value="b2" data-parent="b">Subdomain of B 2</option>
            </select>
        </div>
    </fieldset>
`;

let subdomainFilter;
let domainFilter;
const eventSpy = jest.fn();

describe("initialisation", () => {
  beforeEach(() => {
    document.body.innerHTML = widget_html;
    subdomainFilter = document.querySelector("#subdomains-filter");
    initDomainFilter();
  });

  test("subdomain select is disabled", () => {
    expect(subdomainFilter).toBeDisabled();
  });

  test("the only option is 'all subdomains'", () => {
    expect(subdomainFilter).toHaveLength(1);
  });
});

describe("after selecting a domain", () => {
  beforeEach(() => {
    document.body.innerHTML = widget_html;

    subdomainFilter = document.querySelector("#subdomains-filter");
    domainFilter = document.querySelector("#domains-filter");

    initDomainFilter();

    // Listen to outgoing events
    domainFilter.parentElement.addEventListener(
      "domain-filter-updates",
      eventSpy
    );

    // Emulate selecting a domain
    domainFilter.value = "a";
    domainFilter.dispatchEvent(new Event("change"));
  });

  test("only the selected domain's options are available", () => {
    const options = subdomainFilter.querySelectorAll("option");

    const values = Array.from(options).map((el) => el.value);

    expect(values).toEqual(["*", "a1", "a2"]);
  });

  test("fires an event with the selected domain and null subdomain", () => {
    expect(eventSpy.mock.calls[0][0].detail).toEqual({
      topLevelDomainValue: "a",
      subdomainValue: null,
      label: "Domain A",
    });
  });

  describe("after selecting a subdomain", () => {
    beforeEach(() => {
      // Emulate selecting a subdomain
      subdomainFilter.value = "a1";
      subdomainFilter.dispatchEvent(new Event("change"));
    });

    test("fires an event with the selected domain/subdomain pair", () => {
      expect(eventSpy.mock.calls[1][0].detail).toEqual({
        topLevelDomainValue: "a",
        subdomainValue: "a1",
        label: "Domain A - Subdomain of A 1",
      });
    });

    describe("after changing to another top level domain", () => {
      beforeEach(() => {
        domainFilter.value = "b";
        domainFilter.dispatchEvent(new Event("change"));
      });

      test("only the new domain's options are available", () => {
        const options = subdomainFilter.querySelectorAll("option");

        const values = Array.from(options).map((el) => el.value);

        expect(values).toEqual(["*", "b1", "b2"]);
      });

      test("selects all subdomains", () => {
        expect(subdomainFilter.value).toEqual("*");
      });

      test("fires an event with the selected domain and null subdomain", () => {
        expect(eventSpy.mock.calls[2][0].detail).toEqual({
          topLevelDomainValue: "b",
          subdomainValue: null,
          label: "Domain B",
        });
      });

      describe("after changing back to the original top level domain", () => {
        beforeEach(() => {
          domainFilter.value = "a";
          domainFilter.dispatchEvent(new Event("change"));
        });

        test("selects all subdomains", () => {
          expect(subdomainFilter.value).toEqual("*");
        });
      });
    });

    describe("after clearing the top level domain", () => {
      beforeEach(() => {
        domainFilter.value = "*";
        domainFilter.dispatchEvent(new Event("change"));
      });

      test("subdomain select is disabled", () => {
        expect(subdomainFilter).toBeDisabled();
      });

      test("the only option is 'all subdomains'", () => {
        expect(subdomainFilter.options).toHaveLength(1);
      });

      test("fires an event with null domain/subdomain", () => {
        expect(eventSpy.mock.calls[2][0].detail).toEqual({
          topLevelDomainValue: null,
          subdomainValue: null,
          label: null,
        });
      });
    });
  });
});

// TODO: clear selected subdomain when choosing parent domain
