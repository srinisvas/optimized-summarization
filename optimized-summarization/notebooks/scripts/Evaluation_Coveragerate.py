import os
import pandas as pd
from collections import Counter

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
reference_directory = '/content/optimized-summarization/optimized-summarization/Normalized-papers'
result_directory = '/content/optimized-summarization/optimized-summarization/LLM_Summaries_3B'

# Identify file pairs
identified_file_pairs = identify_summary_file_pairs_modified(reference_directory, result_directory)
print(f"Found {len(identified_file_pairs)} file pairs for coverage rate calculation.")

# --- 2. Coverage Rate Calculation ---

def read_summary_from_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def calculate_coverage_rate(reference, candidate):
    ref_words = Counter(reference.lower().split())
    cand_words = Counter(candidate.lower().split())

    covered_words_count = 0
    for word in cand_words:
        if word in ref_words:
            covered_words_count += min(cand_words[word], ref_words[word])

    total_ref_words = sum(ref_words.values())

    coverage_rate = covered_words_count / total_ref_words if total_ref_words > 0 else 0
    return coverage_rate

all_coverage_rates = []

for ref_file_path, res_file_path in identified_file_pairs:
    try:
        reference_summary = read_summary_from_file(ref_file_path)
        result_summary = read_summary_from_file(res_file_path)

        coverage = calculate_coverage_rate(reference_summary, result_summary)

        all_coverage_rates.append({
            'reference_file': os.path.basename(ref_file_path),
            'result_file': os.path.basename(res_file_path),
            'coverage_rate': coverage,
        })
    except Exception as e:
        print(f"Error processing pair {os.path.basename(ref_file_path)} and {os.path.basename(res_file_path)}: {e}")

print(f"Processed {len(all_coverage_rates)} file pairs and stored their coverage rates.")

# --- 3. Calculate and Display Average Coverage Rates ---

if all_coverage_rates:
    df_coverage_rates = pd.DataFrame(all_coverage_rates)
    avg_coverage_rate = df_coverage_rates['coverage_rate'].mean()

    print("\n--- Average Coverage Rate Across All Pairs ---")
    print(f"Average Coverage Rate: {avg_coverage_rate:.4f}")
else:
    print("\nNo coverage rates were processed to calculate averages.")

# --- 4. Save Coverage Rates to File ---

evaluation_dir = '/content/optimized-summarization/optimized-summarization/Evaluation'
os.makedirs(evaluation_dir, exist_ok=True)
output_filepath = os.path.join(evaluation_dir, 'Coverage_Rate.csv') # Changed to .csv

if all_coverage_rates:
    df_output = pd.DataFrame({
        'Pair_ID': range(1, len(all_coverage_rates) + 1),
        'Coverage_Rate': [d['coverage_rate'] for d in all_coverage_rates]
    })
    df_output.to_csv(output_filepath, index=False)
    print(f"Coverage rates successfully saved to {output_filepath}")
else:
    print("\nNo coverage rates were processed to save.")
