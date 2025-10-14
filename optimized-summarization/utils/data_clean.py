import re
import os
import json

def clean_and_segment_article(text):
    # 1. Remove references & citations
    text = re.sub(r'\[\s*\d+(?:[\-,]\s*\d+)*\s*\]', '', text)
    text = re.sub(r'\([A-Z][^)]*\d{4}[^)]*\)', '', text)
    text = re.sub(r'\[b\d+\]', '', text)

    # 2. Remove LaTeX/math
    text = re.sub(r'\${1,2}[^$]*\${1,2}', '', text)
    text = re.sub(r'\\\[.*?\\\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', text, flags=re.DOTALL)

    # 3. Normalize
    text = re.sub(r'\s+', ' ', text).strip()

    # 4. Segment by section
    section_split = re.split(
        r'(?mi)(^\s*(?:I{0,3}|V?I{0,3}|[A-Z])[\.\)]?\s*(?:abstract|introduction|literature\s+review|methodology|methods?|results?|discussion|conclusion[s]?|recommendation[s]?)\s*[:\-–]?\s*$)',
        text
    )

    # 5. Return structured dictionary
    structured = {}
    for i in range(1, len(section_split), 2):
        heading = re.sub(r'^\s*\d*[\.\)]?\s*', '', section_split[i].strip()).title()
        content = section_split[i+1].strip()
        structured[heading] = content

    return structured

def normalize_all_jsons(json_folder):
    """
    Reads all JSON files in json_folder, normalizes their main text using clean_and_segment_article,
    and stores them as a dict of dicts.
    Returns:
        dict: {filename (str): normalized_dict}
    """
    normalized_dicts = {}
    for filename in os.listdir(json_folder):
        if filename.lower().endswith('.json'):
            json_path = os.path.join(json_folder, filename)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            main_text = data.get('text') or data.get('body') or json.dumps(data)
            normalized = clean_and_segment_article(main_text)
            normalized_dicts[os.path.splitext(filename)[0]] = normalized
    return normalized_dicts

print(normalize_all_jsons('../papers_json/'))