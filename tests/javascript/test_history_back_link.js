import {
  extractDisplayNameFromDetailsUrn,
  getReferrerLabel,
  initHistoryBackLinks,
  labelFromPath,
  shouldUseHistoryBack,
} from "history-back-link";
import { beforeEach, describe, expect, jest, test } from "@jest/globals";

describe("history back link path labels", () => {
  test("maps search routes and details URNs to descriptive labels", () => {
    expect(labelFromPath("/search")).toBe("search results");
    expect(labelFromPath("/pagination/2")).toBe("search results");
    expect(labelFromPath("/details/database/urn:li:dataset:db1")).toBe("db1");
    expect(
      labelFromPath(
        "/details/table/urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.cica_datamarts.brg_case_type,PROD)"
      )
    ).toBe("brg_case_type");
    expect(labelFromPath("/")).toBe("Home");
  });

  test("falls back to entity type label for opaque container ids", () => {
    expect(labelFromPath("/details/database/urn:li:container:0dcb7860747b546165f4ccc8a9e4141d")).toBe("Database");
  });

  test("returns null for unknown routes", () => {
    expect(labelFromPath("/unknown/route")).toBe(null);
  });
});

describe("details URN display name extraction", () => {
  test("extracts the final table name from dotted URN tuple values", () => {
    const displayName = extractDisplayNameFromDetailsUrn(
      "urn:li:dataset:(urn:li:dataPlatform:dbt,cadet.awsdatacatalog.cica_datamarts.brg_case_type,PROD)"
    );

    expect(displayName).toBe("brg_case_type");
  });

  test("handles encoded URNs", () => {
    const encodedUrn =
      "urn%3Ali%3Adataset%3A(urn%3Ali%3AdataPlatform%3Adbt%2Ccadet.awsdatacatalog.cica_datamarts.brg_case_type%2CPROD)";
    expect(extractDisplayNameFromDetailsUrn(encodedUrn)).toBe("brg_case_type");
  });

  test("falls back to the final urn token for simple URNs", () => {
    expect(extractDisplayNameFromDetailsUrn("urn:li:dataset:db1")).toBe("db1");
  });
});

describe("history back link referrer and click behavior", () => {
  beforeEach(() => {
    document.body.innerHTML = "";
    window.sessionStorage.clear();
  });

  test("uses same-origin referrer to derive a label", () => {
    const label = getReferrerLabel("http://localhost/search?query=nomis", "http://localhost");
    expect(label).toBe("search results");
  });

  test("prefers sessionStorage label for previous page url", () => {
    window.sessionStorage.setItem(
      "historyBackLabelsV1",
      JSON.stringify({
        "http://localhost/details/database/urn:li:container:0dcb7860747b546165f4ccc8a9e4141d":
          "Crown Court dimensional model",
      })
    );

    const label = getReferrerLabel(
      "http://localhost/details/database/urn:li:container:0dcb7860747b546165f4ccc8a9e4141d",
      "http://localhost"
    );
    expect(label).toBe("Crown Court dimensional model");
  });

  test("ignores cross-origin referrer labels", () => {
    const label = getReferrerLabel("https://example.com/search", "http://localhost");
    expect(label).toBe(null);
  });

  test("initialises fallback label when no referrer label is available", () => {
    document.body.innerHTML = `
      <a
        href="/search"
        class="govuk-back-link"
        data-history-back-link="true"
        data-fallback-label="search results"
      >
        Back
      </a>
    `;

    initHistoryBackLinks(document);

    const backLink = document.querySelector("[data-history-back-link='true']");
    expect(backLink.textContent.trim()).toBe("Back to search results");
  });

  test("uses browser history for one-step back when available", () => {
    const historyBackSpy = jest.spyOn(window.history, "back").mockImplementation(() => {});

    document.body.innerHTML = `
      <a
        href="/search"
        class="govuk-back-link"
        data-history-back-link="true"
        data-fallback-label="search results"
      >
        Back
      </a>
    `;

    Object.defineProperty(document, "referrer", {
      configurable: true,
      value: "http://localhost/details/database/foo",
    });

    window.history.pushState({}, "", "/details/table/bar");
    initHistoryBackLinks(document);

    const backLink = document.querySelector("[data-history-back-link='true']");
    const clickEvent = new MouseEvent("click", { bubbles: true, cancelable: true });
    backLink.dispatchEvent(clickEvent);

    expect(shouldUseHistoryBack(document.referrer, window.history.length, window.location.origin)).toBe(true);
    expect(clickEvent.defaultPrevented).toBe(true);
    expect(historyBackSpy).toHaveBeenCalled();

    historyBackSpy.mockRestore();
  });

  test("uses browser history even when no label can be resolved", () => {
    Object.defineProperty(document, "referrer", {
      configurable: true,
      value: "http://localhost/unknown/route",
    });

    expect(shouldUseHistoryBack(document.referrer, 2, "http://localhost")).toBe(true);
  });
});
