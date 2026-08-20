const HISTORY_BACK_LINK_SELECTOR = '[data-history-back-link="true"]';
const SESSION_LABELS_KEY = "historyBackLabelsV1";

function toDisplayLabel(value) {
  return value
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
}

function normaliseRouteSegment(segment) {
  return toDisplayLabel(segment.replace(/[_-]+/g, " "));
}

function decodeUrlComponent(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function looksLikeOpaqueIdentifier(value) {
  return /^[a-f0-9]{24,}$/i.test(value);
}

function getLabelStore() {
  try {
    const rawLabels = window.sessionStorage.getItem(SESSION_LABELS_KEY);
    if (!rawLabels) {
      return {};
    }

    const parsed = JSON.parse(rawLabels);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function setLabelStore(store) {
  try {
    window.sessionStorage.setItem(SESSION_LABELS_KEY, JSON.stringify(store));
  } catch {
    // Ignore storage failures (private mode, disabled storage, quota errors).
  }
}

function normaliseAbsoluteUrl(rawUrl, locationOrigin = window.location.origin) {
  if (!rawUrl) {
    return null;
  }

  try {
    const parsedUrl = new URL(rawUrl, locationOrigin);
    if (parsedUrl.origin !== locationOrigin) {
      return null;
    }

    parsedUrl.hash = "";
    return parsedUrl.toString();
  } catch {
    return null;
  }
}

function getCurrentPageLabel() {
  const pageHeading = document.querySelector("#main-content h1") || document.querySelector("h1");
  const label = pageHeading?.textContent?.trim();

  return label || null;
}

function storeCurrentPageLabel() {
  const pageLabel = getCurrentPageLabel();
  const currentUrl = normaliseAbsoluteUrl(window.location.href);

  if (!pageLabel || !currentUrl) {
    return;
  }

  const labels = getLabelStore();
  labels[currentUrl] = pageLabel;
  setLabelStore(labels);
}

function getStoredReferrerLabel(documentReferrer = document.referrer, locationOrigin = window.location.origin) {
  const referrerUrl = normaliseAbsoluteUrl(documentReferrer, locationOrigin);
  if (!referrerUrl) {
    return null;
  }

  const labels = getLabelStore();
  return labels[referrerUrl] || null;
}

export function extractDisplayNameFromDetailsUrn(rawUrn) {
  if (!rawUrn) {
    return null;
  }

  const decodedUrn = decodeUrlComponent(rawUrn.replace(/\.csv$/, ""));
  const bracketedEntityMatch = decodedUrn.match(/urn:li:[^:]+:\(([^)]+)\)/);

  let candidate;
  if (bracketedEntityMatch && bracketedEntityMatch[1]) {
    const urnParts = bracketedEntityMatch[1].split(",").map((part) => part.trim());
    candidate = urnParts.length > 1 ? urnParts[1] : urnParts[urnParts.length - 1];
  } else {
    const colonParts = decodedUrn.split(":").filter(Boolean);
    candidate = colonParts[colonParts.length - 1];
  }

  if (!candidate) {
    return null;
  }

  const trimmedCandidate = candidate.trim();
  if (!trimmedCandidate || looksLikeOpaqueIdentifier(trimmedCandidate)) {
    return null;
  }

  // Prefer the entity name when the candidate contains a dotted namespace path.
  return trimmedCandidate.includes(".") ? trimmedCandidate.split(".").pop() : trimmedCandidate;
}

export function labelFromPath(pathname) {
  if (!pathname || pathname === "/") {
    return "Home";
  }

  if (pathname.startsWith("/search") || pathname.startsWith("/pagination/")) {
    return "search results";
  }

  if (pathname.startsWith("/userguide/")) {
    return "User guide";
  }

  if (pathname.startsWith("/metadata_specification")) {
    return "Metadata specification";
  }

  if (pathname.startsWith("/cookies")) {
    return "Cookies";
  }

  if (pathname.startsWith("/accessibility_statement")) {
    return "Accessibility statement";
  }

  if (pathname.startsWith("/details/")) {
    const pathParts = pathname.split("/").filter(Boolean);
    if (pathParts.length > 2) {
      const entityName = extractDisplayNameFromDetailsUrn(pathParts[2]);
      if (entityName) {
        return entityName;
      }
    }

    if (pathParts.length > 1) {
      return normaliseRouteSegment(pathParts[1]);
    }

    return "Details";
  }

  return null;
}

export function getReferrerLabel(documentReferrer = document.referrer, locationOrigin = window.location.origin) {
  if (!documentReferrer) {
    return null;
  }

  const storedReferrerLabel = getStoredReferrerLabel(documentReferrer, locationOrigin);
  if (storedReferrerLabel) {
    return storedReferrerLabel;
  }

  try {
    const referrerUrl = new URL(documentReferrer);
    if (referrerUrl.origin !== locationOrigin) {
      return null;
    }

    return labelFromPath(referrerUrl.pathname);
  } catch {
    return null;
  }
}

export function shouldUseHistoryBack(
  documentReferrer = document.referrer,
  historyLength = window.history.length,
  locationOrigin = window.location.origin
) {
  if (!documentReferrer || historyLength <= 1) {
    return false;
  }

  try {
    const referrerUrl = new URL(documentReferrer);
    return referrerUrl.origin === locationOrigin;
  } catch {
    return false;
  }
}

function setBackLinkLabel(linkElement, label) {
  const backLabel = label.includes("_") ? label : toDisplayLabel(label);
  const normalisedBackLabel = backLabel.toLowerCase();

  if (normalisedBackLabel === "search for data assets" || normalisedBackLabel === "search results") {
    linkElement.textContent = "Back to search results";
  } else {
    linkElement.textContent = `Back to ${backLabel}`;
  }
}

function initialiseLink(linkElement) {
  if (linkElement.dataset.historyBackInitialised === "true") {
    return;
  }

  const fallbackLabel = linkElement.dataset.fallbackLabel || "previous page";
  const referrerLabel = getReferrerLabel();

  setBackLinkLabel(linkElement, referrerLabel || fallbackLabel);

  linkElement.addEventListener("click", (event) => {
    if (shouldUseHistoryBack()) {
      event.preventDefault();
      window.history.back();
    }
  });

  linkElement.dataset.historyBackInitialised = "true";
}

export function initHistoryBackLinks(root = document) {
  const backLinks = root.querySelectorAll(HISTORY_BACK_LINK_SELECTOR);
  backLinks.forEach(initialiseLink);
}

if (typeof document !== "undefined") {
  storeCurrentPageLabel();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initHistoryBackLinks());
  } else {
    initHistoryBackLinks();
  }
}
