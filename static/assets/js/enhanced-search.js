/**
 * Enhance the domain filter to include a subdomain input in addition
 * to the domain filter. When a domain is selected, the widget should
 * dynamically populate the subdomain options, and when a domain is
 * cleared, the subdomain filter should be disabled.
 *
 * Note: This widget does not automatically refresh the results - the user
 * has to hit "Apply filters" first.
 */

const ALL_DOMAINS_VALUE = "";

export const initDomainFilter = () => {
  const subdomainSelect = document.querySelector("#id_subdomain");
  const topLevelDomainSelect = document.querySelector("#id_domain");
  const subdomainGroup = document.querySelector(".js-required");

  if (subdomainSelect === null || topLevelDomainSelect === null) {
    return;
  }

  subdomainGroup.style.display = "block";

  new DomainFilter(topLevelDomainSelect, subdomainSelect);
};

class DomainFilter {
  constructor(topLevelDomainSelect, subdomainSelect) {
    this.topLevelDomainSelect = topLevelDomainSelect;
    this.subdomainSelect = subdomainSelect;
    this.options = this.#extractSubdomainOptions();

    if (this.isWildcardTopLevelDomain()) {
      this.#onClearTopLevelDomain();
    } else {
      const selectedDomain = this.topLevelDomainSelect.value;
      this.#onSelectTopLevelDomain(selectedDomain, false);
    }

    topLevelDomainSelect.addEventListener("change", () =>
      this.#onChangeDomain()
    );
    subdomainSelect.addEventListener("change", () => this.#notify());
  }

  get state() {
    const topLevelDomainOption = this.topLevelDomainSelect.selectedOptions[0];
    const subdomainOption = this.subdomainSelect.selectedOptions[0];

    if (this.isWildcardTopLevelDomain()) {
      return {
        topLevelDomainValue: null,
        subdomainValue: null,
        label: null,
      };
    } else if (this.isWildcardSubdomain()) {
      return {
        topLevelDomainValue: this.topLevelDomainSelect.value,
        subdomainValue: null,
        label: topLevelDomainOption.label,
      };
    } else {
      return {
        topLevelDomainValue: this.topLevelDomainSelect.value,
        subdomainValue: subdomainOption.value,
        label: `${topLevelDomainOption.label} - ${subdomainOption.label}`,
      };
    }
  }

  #onChangeDomain() {
    if (this.isWildcardTopLevelDomain()) {
      this.#onClearTopLevelDomain();
    } else {
      const selectedDomain = this.topLevelDomainSelect.value;
      this.#onSelectTopLevelDomain(selectedDomain, true);
    }

    this.#notify();
  }

  #onSelectTopLevelDomain(selectedDomain, reset) {
    this.subdomainSelect.disabled = false;
    this.#setSubdomainOptions(this.options[selectedDomain], reset);
  }

  #onClearTopLevelDomain() {
    this.#setSubdomainOptions([]);
    this.subdomainSelect.disabled = true;
  }

  isWildcardSubdomain() {
    return this.subdomainSelect.value === ALL_DOMAINS_VALUE;
  }

  isWildcardTopLevelDomain() {
    return this.topLevelDomainSelect.value === ALL_DOMAINS_VALUE;
  }

  #setSubdomainOptions(newOptionElements, reset) {
    const existingOptionElements =
      this.subdomainSelect.querySelectorAll("option");

    existingOptionElements.forEach((option) => {
      if (option.value != ALL_DOMAINS_VALUE) {
        option.parentNode.removeChild(option);
        if (reset) {
          option.selected = false;
        }
      }
    });

    if (newOptionElements === undefined) {
      return;
    }

    newOptionElements.forEach((option) => {
      this.subdomainSelect.appendChild(option);
    });
  }

  #extractSubdomainOptions() {
    var options = {};
    var optionElements = this.subdomainSelect.querySelectorAll("option");

    optionElements.forEach((option) => {
      var parent = option.getAttribute("data-parent");
      options[parent] = options[parent] || [];
      options[parent].push(option);
    });

    return options;
  }

  /**
   * Emit a custom event whenever a new selection is made, so
   * that other parts of the UI can respond to this in real time.
   */
  #notify() {
    const event = new CustomEvent("domain-filter-updates", {
      detail: this.state,
    });

    this.topLevelDomainSelect.parentElement.dispatchEvent(event);
  }
}
