import re
import os
import json

# ---------- Regex Patterns ----------
BRACKETED_CITATION_RE = re.compile(r'\[\s*\d+(?:[\-,]\s*\d+)*\s*\]')
PAREN_YEAR_CITATION_RE = re.compile(r'\([A-Z][^)]*\d{4}[^)]*\)')
FIGURE_REF_RE = re.compile(r'Fig(?:ure)?\s*\d+|Table\s*\d+', re.IGNORECASE)
INLINE_FORMULA_RE = re.compile(r'\${1,2}[^$]*\${1,2}')
INLINE_EQUATION_RE = re.compile(r'\\\[.*?\\\]', flags=re.DOTALL)
LATEX_ENV_RE = re.compile(r'\\begin\{.*?\}.*?\\end\{.*?\}', flags=re.DOTALL)
NUMERIC_RE = re.compile(r'\b\d+(\.\d+)?\b')
LEADING_NUMBERING_RE = re.compile(r'^\s*(?:[IVXLCDM]+\.?|[A-Z]\.?|\d+(\.\d+)*\.?)?[\s:)\.-]*', re.MULTILINE)
LINE_LEADING_ENUM_RE = re.compile(r'(?m)^\s*(?:[a-zA-Z]|\d+)[\)\.]\s+')
MULTISPACE_RE = re.compile(r'[ \t]+')
MULTINEWLINE_RE = re.compile(r'\n{2,}')

# ---------- Cleaning Functions ----------
def clean_text(t: str) -> str:
    if not t:
        return ""
    t = BRACKETED_CITATION_RE.sub("", t)
    t = PAREN_YEAR_CITATION_RE.sub("", t)
    t = FIGURE_REF_RE.sub("", t)
    t = INLINE_FORMULA_RE.sub("", t)
    t = INLINE_EQUATION_RE.sub("", t)
    t = LATEX_ENV_RE.sub("", t)
    t = NUMERIC_RE.sub("", t)
    t = LEADING_NUMBERING_RE.sub("", t)
    t = LINE_LEADING_ENUM_RE.sub("", t)
    t = MULTISPACE_RE.sub(" ", t)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = MULTINEWLINE_RE.sub("\n\n", t)
    return t.strip()

def simplify_paper(paper: dict) -> dict:
    title = clean_text(paper.get("title", ""))
    out_sections = []

    abstract = paper.get("abstract", "")
    if abstract:
        out_sections.append({"title": "Abstract", "content": clean_text(abstract)})

    for sec in paper.get("sections", []):
        heading = clean_text(sec.get("heading", "Section"))
        text = clean_text(sec.get("text", ""))
        if heading or text:
            out_sections.append({"title": heading or "Section", "content": text})

    return {"title": title, "sections": out_sections}

# ---------- Process All JSONs ----------
def normalize_all_jsons(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cleaned = simplify_paper(data)
            output_path = os.path.join(output_folder, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, ensure_ascii=False, indent=2)
            print(f"Processed & saved: {filename}")

# ---------- 🔹 Paths ----------
INPUT_DIR = '/content/drive/MyDrive/optimized-summarization/optimized-summarization/papers_json/'
OUTPUT_DIR = '/content/drive/MyDrive/optimized-summarization/normalized_papers/'

# ---------- Run ----------
normalize_all_jsons(INPUT_DIR, OUTPUT_DIR)
