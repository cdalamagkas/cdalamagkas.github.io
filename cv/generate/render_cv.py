#!/usr/bin/env python3
"""Render cv-{lang}.tex from the website's data/{lang}/ YAML.

Usage:
    python cv/generate/render_cv.py --lang en --out cv/cv-en.tex
    python cv/generate/render_cv.py --lang gr --out cv/cv-gr.tex
"""
import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml
from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from filters import latex_escape, markdown_and_escape

SCRIPT_DIR = Path(__file__).resolve().parent
CV_ROOT = SCRIPT_DIR.parent
REPO_ROOT = CV_ROOT.parent

LABELS = {
    "en": {
        "now": "Now",
        "location": "Location",
        "doc_subject": "Curriculum Vitae",
        "section_education": "Education",
        "section_experience": "Experience",
        "section_certifications": "Professional Certifications",
        "section_skills": "Skills",
        "section_activities": "Voluntary Activities and Memberships",
    },
    "gr": {
        "now": "Τωρα",
        "location": "Τοποθεσία",
        "doc_subject": "Βιογραφικό",
        "section_education": "Εκπαιδευση",
        "section_experience": "Επαγγελματικη εμπειρια",
        "section_certifications": "Επαγγελματικες Πιστοποιησεις",
        "section_skills": "Δεξιοτητες",
        "section_activities": "Εθελοντικες Δραστηριοτητες και Συνδρομες",
    },
}

# Social link display names (as used in about.yaml's socialLinks) that the
# CV's \contact line needs. Missing any of these is a hard error rather
# than a silently blank contact line.
REQUIRED_SOCIAL_LINKS = ["Github", "LinkedIn", "ORCID"]


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def date_range(start, end, now_label):
    return f"{start} - {end}" if end else f"{start} - {now_label}"


def with_name_override(item):
    """Apply an optional `cv.name` override (e.g. an English-only label, or
    an expanded form of a short website-facing name) without mutating the
    original dict."""
    override = item.get("cv", {}).get("name")
    return {**item, "name": override} if override else item


def social_url(social_links, name):
    for link in social_links:
        if link.get("name") == name:
            return link["url"]
    raise ValueError(
        f"about.yaml socialLinks is missing a '{name}' entry, required to build the CV contact line"
    )


def build_contact(author, about, hugo_config):
    social_links = about.get("socialLinks", [])
    github_url = social_url(social_links, "Github")
    linkedin_url = social_url(social_links, "LinkedIn")
    orcid_url = social_url(social_links, "ORCID")

    return {
        "mobile": author["contactInfo"]["phone"],
        "email": author["contactInfo"]["email"],
        "homepage": hugo_config["baseURL"],
        # mycv.cls's \linkedin/\github/\orcid build the href themselves
        # (https://www.#1, https://github.com/#1, https://orcid.org/#1),
        # so we pass the bare path/id, not the full URL.
        "linkedin": urlparse(linkedin_url).netloc.removeprefix("www.")
        + urlparse(linkedin_url).path.rstrip("/"),
        "github": urlparse(github_url).path.strip("/"),
        "orcid": urlparse(orcid_url).path.strip("/"),
    }


def build_context(lang):
    data_dir = REPO_ROOT / "data" / lang
    sections_dir = data_dir / "sections"

    author = load_yaml(data_dir / "author.yaml")
    about = load_yaml(sections_dir / "about.yaml")
    experiences = load_yaml(sections_dir / "experiences.yaml").get("experiences", [])
    educations = load_yaml(sections_dir / "educations.yaml").get("degrees", [])
    skills = load_yaml(sections_dir / "skills.yaml").get("skills", [])
    activities = load_yaml(sections_dir / "activities.yaml").get("activities", [])
    hugo_config = load_yaml(REPO_ROOT / "hugo.yaml")

    now_label = LABELS[lang]["now"]

    # An entry only appears in the generated CV if it has a `cv:` block -
    # this is the single opt-in mechanism across every section.
    education_entries = [d for d in educations if d.get("cv")]
    activity_entries = [a for a in activities if a.get("cv")]
    certification_entries = [
        with_name_override(b)
        for b in about.get("badges", [])
        if b.get("type") == "certification" and b.get("cv")
    ]

    experience_entries = []
    for exp in experiences:
        company = exp["company"]
        if not company.get("cv"):
            continue
        display_company = with_name_override(company)
        for position in exp["positions"]:
            experience_entries.append(
                {
                    "company": display_company,
                    "position": position,
                    "dates": date_range(
                        position["start"], position.get("end"), now_label
                    ),
                }
            )

    skill_rows = []
    for skill in skills:
        cv = skill.get("cv")
        if not cv:
            continue
        # "terms", not "items" - dicts have a built-in `.items` method that
        # would otherwise shadow a same-named key under Jinja's attribute
        # lookup (row.items resolves to the bound method, not the key).
        skill_rows.append({"label": cv.get("label", skill["name"]), "terms": cv["items"]})

    return {
        "lang": lang,
        "labels": LABELS[lang],
        "author": author,
        "about": about,
        "contact": build_contact(author, about, hugo_config),
        "education_entries": education_entries,
        "experience_entries": experience_entries,
        "certification_entries": certification_entries,
        "skill_rows": skill_rows,
        "activity_entries": activity_entries,
    }


def render(lang, out_path):
    env = Environment(
        loader=FileSystemLoader(str(SCRIPT_DIR / "templates")),
        block_start_string="\\BLOCK{",
        block_end_string="}",
        variable_start_string="\\VAR{",
        variable_end_string="}",
        comment_start_string="\\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    env.filters["tex"] = latex_escape
    env.filters["md"] = markdown_and_escape

    template = env.get_template("cv.tex.jinja")
    context = build_context(lang)
    rendered = template.render(**context)
    if lang == "en":
        check_no_greek_script(rendered)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")


def check_no_greek_script(rendered_tex):
    """pdflatex (used for the English CV) can't render Greek-script glyphs
    without full Unicode font support. Fail loudly instead of producing a
    tex file that pdflatex will choke on - add a `cv.name`/`cv.title`
    English-only override on the offending YAML entry instead."""
    greek_chars = {ch for ch in rendered_tex if "Ͱ" <= ch <= "Ͽ"}
    if greek_chars:
        raise ValueError(
            "English CV source contains Greek-script characters "
            f"({''.join(sorted(greek_chars))!r}), which pdflatex cannot render. "
            "Add an English-only override (e.g. cv.name / cv.title) on the "
            "relevant data/en/ YAML entry."
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", required=True, choices=["en", "gr"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    render(args.lang, args.out)


if __name__ == "__main__":
    main()
