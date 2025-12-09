import scipdf
import json
import os

def extract_text_from_pdf(pdf_path):
    article_dict = scipdf.parse_pdf_to_dict(pdf_path)
    return article_dict

def save_json(data, json_path):
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def process_all_papers(papers_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for filename in os.listdir(papers_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(papers_dir, filename)
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(output_dir, json_filename)
            try:
                data = extract_text_from_pdf(pdf_path)
                save_json(data, json_path)
                print(f"Processed: {filename} -> {json_filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")


input_dir = '../papers/'
output_dir = '../papers_json/'

process_all_papers(input_dir, output_dir)
