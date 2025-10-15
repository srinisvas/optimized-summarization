import json
import re
import os

# ---------- Regex Definitions ----------
BRACKETED_CITATION_RE = re.compile(r"\[[0-9,\s\-–]+\]")
PAREN_YEAR_CITATION_RE = re.compile(
    r"\((?:[A-Z][A-Za-z\-\.' ]+(?:et al\.)?,?\s*)?(?:19|20)\d{2}[a-z]?(?:;\s*(?:[A-Z][A-Za-z\-\.' ]+(?:et al\.)?,?\s*)?(?:19|20)\d{2}[a-z]?)*\)",
    re.VERBOSE
)
LEADING_NUMBERING_RE = re.compile(r"^\s*(?:\(?[IVXLCDMivxlcdm]+\)?\.?|[A-Z]\.|[0-9]+(?:\.[0-9]+)*\.?)\s*[-:\.)]?\s*")
FIGURE_REF_RE = re.compile(r"(figure|fig\.?|table|tbl\.?)\s*\d+", re.IGNORECASE)
INLINE_FORMULA_RE = re.compile(r"\$[^$]+\$|\\\([^\\)]+\\\)|\\\[[^\\]]+\\\]")
INLINE_EQUATION_RE = re.compile(r"[A-Za-z]*=[A-Za-z0-9\+\-\*/\^\(\)\[\]\s]+")
NUMERIC_RE = re.compile(r"\b\d{1,4}\b")
REFERENCE_HEADING_RE = re.compile(r"(?i)\b(references?|bibliography)\b")
MULTISPACE_RE = re.compile(r"[ \t]+")
MULTINEWLINE_RE = re.compile(r"\n{3,}")

# ---------- Cleaning Functions ----------
def clean_heading(h: str) -> str:
    if not h:
        return ""
    cleaned = LEADING_NUMBERING_RE.sub("", h).strip(" :.-\u2013\u2014")
    return cleaned if cleaned else h.strip()

def clean_text(t: str) -> str:
    if not t:
        return ""
    t = BRACKETED_CITATION_RE.sub("", t)
    t = PAREN_YEAR_CITATION_RE.sub("", t)
    t = FIGURE_REF_RE.sub("", t)
    t = INLINE_FORMULA_RE.sub("", t)
    t = INLINE_EQUATION_RE.sub("", t)
    t = NUMERIC_RE.sub("", t)
    t = MULTISPACE_RE.sub(" ", t)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = MULTINEWLINE_RE.sub("\n\n", t)
    return t.strip()

def simplify_paper(paper):
    title = clean_heading(paper.get("title", "").strip())
    out_sections = []

    abstract = (paper.get("abstract") or "").strip()
    if abstract:
        out_sections.append({"title": "Abstract", "content": clean_text(abstract)})

    for sec in paper.get("sections", []):
        heading = clean_heading(sec.get("heading", ""))
        if REFERENCE_HEADING_RE.search(heading or ""):
            continue
        text = clean_text(sec.get("text", ""))
        if text:
            out_sections.append({"title": heading or "Section", "content": text})

    return {"title": title, "sections": out_sections}

# ---------- 🔹 Test for One Paper ----------
input_file = r"C:\Users\bhara\OneDrive - Texas Tech University\Documents\Ramya\NLP\A Bibliometric View of AI Ethics Development.json"
output_file = input_file.replace(".json", "_cleaned.json")

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned = simplify_paper(data)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)

print(f"✅ Paper cleaned and saved as: {output_file}")
