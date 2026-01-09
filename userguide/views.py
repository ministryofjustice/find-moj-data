import os
import re
from collections.abc import Iterator
from dataclasses import dataclass, field

import markdown
from django.http import Http404
from django.shortcuts import render
from django.utils.text import slugify
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

DOCS_DIR = os.path.join(os.path.dirname(__file__), "content")


@dataclass
class SidebarItem:
    header: str
    header_slug: str
    subheader: list


@dataclass
class Sidebar:
    sidebar: list[SidebarItem] = field(default_factory=list)
    slug_to_header: dict = field(default_factory=dict)

    def add_item(self, item: SidebarItem):
        """Appends a SidebarItem to the sidebar list."""
        self.sidebar.append(item)
        self.slug_to_header[item.header_slug] = item.header

    def __iter__(self) -> Iterator[tuple[str, str, list[str]]]:
        """Makes the Sidebar iterable."""
        for item in self.sidebar:
            yield (
                item.header,
                item.header_slug,
                item.subheader,
            )


class CustomClassProcessor(Treeprocessor):
    """
    Adds gov.uk classes to elements in the markdown file contents.
    """

    def generate_id(self, text):
        return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()

    def run(self, root):
        for element in root.iter():
            tag_class_map = {
                "h1": "govuk-heading-xl",
                "h2": "govuk-heading-l",
                "h3": "govuk-heading-m",
                "ul": "govuk-list govuk-list--bullet govuk-list--spaced",
                "a": "govuk-link govuk-link--no-visited-state govuk-link--no-underline",
                "table": "govuk-table",
                "thead": "govuk-table__header",
                "tr": "govuk-table__row",
                "td": "govuk-table__cell govuk-body-s",
                "tbody": "govuk-table__body",
            }

            if element.tag in tag_class_map:
                element.set("class", tag_class_map[element.tag])
                if element.tag in ["h1", "h2", "h3"]:
                    element.set("id", self.generate_id(element.text))


class CustomClassExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(CustomClassProcessor(md), "govuk_class", 5)


def make_side_bar_items() -> Sidebar:
    """
    Loads all markdown files in the content directory
    and creates the sidebar object
    """
    sidebar = Sidebar()
    docs = sorted(doc for doc in os.listdir(DOCS_DIR) if doc.endswith(".md"))
    for file in docs:
        with open(os.path.join(DOCS_DIR, file), encoding="utf-8") as f:
            content = f.read()
            subheader = []
            for line in content.split("\n"):
                if line.startswith("# "):  # Header level 1
                    header = line[2:].strip()
                elif line.startswith("##"):  # Header level 2 or higher
                    subheader.append(line[3:].strip())

            sidebar.add_item(
                SidebarItem(
                    header=header,
                    header_slug=slugify(header),
                    subheader=subheader,
                )
            )
    return sidebar


def get_markdown_content(filename) -> str:
    """The filename should be the header slug without the .md extension, and in the same case.
    i.e, "# About" for "About.md".
    """
    file_path = os.path.normpath(os.path.join(DOCS_DIR, filename + ".md"))
    if not file_path.startswith(DOCS_DIR):
        raise Http404("Page not found")
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    else:
        raise Http404("Page not found")


def userguide_view(request, slug="about"):
    # Generate a sidebar menu from the file structure
    sidebar_items = make_side_bar_items()
    original_header = sidebar_items.slug_to_header.get(slug, slug)
    content = get_markdown_content(original_header)
    html_output = markdown.markdown(
        content,
        extensions=[
            "fenced_code",
            "attr_list",
            CustomClassExtension(),
            "tables",
        ],
    )
    return render(
        request,
        "userguide_page.html",
        {"content": html_output, "sidebar": sidebar_items},
    )
