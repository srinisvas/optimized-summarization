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
reference_directory = '/content/optimized-summarization/optimized-summarization/LLM summaries'
result_directory = '/content/optimized-summarization/optimized-summarization/LLM_Summaries_3B'

# Identify file pairs
identified_file_pairs = identify_summary_file_pairs_modified(reference_directory, result_directory)
print(f"Found {len(identified_file_pairs)} file pairs for ROUGE score calculation.")

# --- 2. ROUGE Score Calculation ---

def read_summary_from_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
all_rouge_scores = []

for ref_file_path, res_file_path in identified_file_pairs:
    try:
        reference_summary = read_summary_from_file(ref_file_path)
        result_summary = read_summary_from_file(res_file_path)

        scores = scorer.score(reference_summary, result_summary)

        rouge1_scores = scores['rouge1']
        rougel_scores = scores['rougeL']

        all_rouge_scores.append({
            'reference_file': os.path.basename(ref_file_path),
            'result_file': os.path.basename(res_file_path),
            'rouge1_precision': rouge1_scores.precision,
            'rouge1_recall': rouge1_scores.recall,
            'rouge1_fmeasure': rouge1_scores.fmeasure,
            'rougeL_precision': rougel_scores.precision,
            'rougeL_recall': rougel_scores.recall,
            'rougeL_fmeasure': rougel_scores.fmeasure,
        })
    except Exception as e:
        print(f"Error processing pair {os.path.basename(ref_file_path)} and {os.path.basename(res_file_path)}: {e}")

print(f"Processed {len(all_rouge_scores)} file pairs and stored their ROUGE scores.")

# --- 3. Calculate and Display Average ROUGE Scores ---

if all_rouge_scores:
    df_scores = pd.DataFrame(all_rouge_scores)
    avg_rouge1_precision = df_scores['rouge1_precision'].mean()
    avg_rouge1_recall = df_scores['rouge1_recall'].mean()
    avg_rouge1_fmeasure = df_scores['rouge1_fmeasure'].mean()
    avg_rougeL_precision = df_scores['rougeL_precision'].mean()
    avg_rougeL_recall = df_scores['rougeL_recall'].mean()
    avg_rougeL_fmeasure = df_scores['rougeL_fmeasure'].mean()

    print("\n--- Average ROUGE Scores Across All Pairs ---")
    print(f"Average ROUGE-1: P={avg_rouge1_precision:.4f}, R={avg_rouge1_recall:.4f}, F1={avg_rouge1_fmeasure:.4f}")
    print(f"Average ROUGE-L: P={avg_rougeL_precision:.4f}, R={avg_rougeL_recall:.4f}, F1={avg_rougeL_fmeasure:.4f}")
else:
    print("\nNo ROUGE scores were processed to calculate averages.")

# --- 4. Save ROUGE Scores to File ---

evaluation_dir = '/content/optimized-summarization/optimized-summarization/Evaluation'
os.makedirs(evaluation_dir, exist_ok=True)
output_filepath = os.path.join(evaluation_dir, 'ROGUE_Score.txt')

with open(output_filepath, 'w') as f:
    f.write("--- Individual ROUGE Scores ---\n")
    for i, scores_dict in enumerate(all_rouge_scores):
        f.write(f"\nPair {i+1}: Reference: {scores_dict['reference_file']}, Result: {scores_dict['result_file']}\n")
        f.write(f"  ROUGE-1: P={scores_dict['rouge1_precision']:.4f}, R={scores_dict['rouge1_recall']:.4f}, F1={scores_dict['rouge1_fmeasure']:.4f}\n")
        f.write(f"  ROUGE-L: P={scores_dict['rougeL_precision']:.4f}, R={scores_dict['rougeL_recall']:.4f}, F1={scores_dict['rougeL_fmeasure']:.4f}\n")

    if all_rouge_scores:
        f.write("\n--- Average ROUGE Scores Across All Pairs ---\n")
        f.write(f"Average ROUGE-1: P={avg_rouge1_precision:.4f}, R={avg_rouge1_recall:.4f}, F1={avg_rouge1_fmeasure:.4f}\n")
        f.write(f"Average ROUGE-L: P={avg_rougeL_precision:.4f}, R={avg_rougeL_recall:.4f}, F1={avg_rougeL_fmeasure:.4f}\n")
    else:
        f.write("\nNo ROUGE scores were processed to calculate averages.\n")

print(f"ROUGE scores successfully saved to {output_filepath}")
