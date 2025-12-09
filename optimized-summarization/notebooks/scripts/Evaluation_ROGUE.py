import os
import pandas as pd
from rouge_score import rouge_scorer

# Ensure rouge-score is installed
!pip install -q rouge-score

# --- 1. File Identification ---

def identify_summary_file_pairs_modified(ref_dir, res_dir, max_pairs=100):
    ref_files_full_paths = [os.path.join(ref_dir, f) for f in os.listdir(ref_dir) if os.path.isfile(os.path.join(ref_dir, f)) and not f.endswith('.gitkeep')]
    res_files_full_paths = [os.path.join(res_dir, f) for f in os.listdir(res_dir) if os.path.isfile(os.path.join(res_dir, f)) and not f.endswith('.gitkeep')]

    result_basenames = {os.path.splitext(os.path.basename(f))[0] for f in res_files_full_paths}

    file_pairs = []
    for ref_file_path in ref_files_full_paths:
        if len(file_pairs) >= max_pairs:
            break

        ref_basename = os.path.splitext(os.path.basename(ref_file_path))[0]

        if ref_basename in result_basenames:
            corresponding_res_file = next((f for f in res_files_full_paths if os.path.splitext(os.path.basename(f))[0] == ref_basename), None)
            if corresponding_res_file:
                file_pairs.append((ref_file_path, corresponding_res_file))
    return file_pairs

# Define the directories
reference_directory = '/content/optimized-summarization/optimized-summarization/Reference-Summary'
result_directory = '/content/optimized-summarization/optimized-summarization/LLM_Summaries_3B'

# Identify file pairs
identified_file_pairs = identify_summary_file_pairs_modified(reference_directory, result_directory)
print(f"Found {len(identified_file_pairs)} file pairs for ROUGE score calculation.")

# --- 2. ROUGE Score Calculation ---

def read_summary_from_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
all_rouge_scores = []

for ref_file_path, res_file_path in identified_file_pairs:
    try:
        reference_summary = read_summary_from_file(ref_file_path)
        result_summary = read_summary_from_file(res_file_path)

        scores = scorer.score(reference_summary, result_summary)

        all_rouge_scores.append({
            'reference_file': os.path.basename(ref_file_path),
            'result_file': os.path.basename(res_file_path),
            'rouge1_recall': scores['rouge1'].recall,
        })
    except Exception as e:
        print(f"Error processing pair {os.path.basename(ref_file_path)} and {os.path.basename(res_file_path)}: {e}")

print(f"Processed {len(all_rouge_scores)} file pairs and stored their ROUGE scores.")

# --- 3. Calculate and Display Average ROUGE Scores ---

if all_rouge_scores:
    df_scores = pd.DataFrame(all_rouge_scores)
    avg_rouge1_recall = df_scores['rouge1_recall'].mean()

    print("\n--- Average ROUGE Scores Across All Pairs ---")
    print(f"Average ROUGE-1 Recall: R={avg_rouge1_recall:.4f}")
else:
    print("\nNo ROUGE scores were processed to calculate averages.")

# --- 4. Save ROUGE Scores to File ---

evaluation_dir = '/content/optimized-summarization/optimized-summarization/Evaluation'
os.makedirs(evaluation_dir, exist_ok=True)
output_filepath = os.path.join(evaluation_dir, 'ROGUE_Recall_Scores.csv') # Changed filename and content

if all_rouge_scores:
    df_output = pd.DataFrame({
        'Pair_ID': range(1, len(all_rouge_scores) + 1),
        'rouge1_recall': [d['rouge1_recall'] for d in all_rouge_scores],
    })
    df_output.to_csv(output_filepath, index=False)
    print(f"ROUGE scores successfully saved to {output_filepath}")
else:
    print("\nNo ROUGE scores were processed to save.")
