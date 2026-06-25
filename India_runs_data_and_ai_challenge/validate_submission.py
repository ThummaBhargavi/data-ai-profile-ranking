import os
import csv
import re
import sys

# Core structure parameters defined by the challenge documentation
EXPECTED_COLS = ["candidate_id", "rank", "score", "reasoning"]
ID_REGEX = re.compile(r"^CAND_[0-9]{7}$")
TOTAL_ROWS_TARGET = 100

def check_csv_formatting(file_path):
    print(f"--> Verifying file data structure at: {file_path}")
    issues_found = []
    
    if not os.path.exists(file_path):
        return False
        
    if not file_path.lower().endswith(".csv"):
        issues_found.append("File extension is wrong. Must be a .csv file.")
        
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as src:
            csv_reader = csv.reader(src)
            try:
                csv_header = next(csv_reader)
            except StopIteration:
                issues_found.append("Validation aborted: Target CSV file is completely empty.")
                return display_report(issues_found)
                
            # Cross-reference headers matching strict parameters
            if csv_header != EXPECTED_COLS:
                issues_found.append(f"Header mismatch anomaly.\nExpected: {EXPECTED_COLS}\nFound: {csv_header}")
                
            counter = 0
            tracked_ids = set()
            tracked_ranks = set()
            
            for line_number, row in enumerate(csv_reader, start=2):
                counter += 1
                if not row:
                    issues_found.append(f"Line {line_number}: Blank row block detected.")
                    continue
                    
                if len(row) != 4:
                    issues_found.append(f"Line {line_number}: Column length mismatch. Found {len(row)} items instead of 4.")
                    continue
                    
                c_id, rank_val, score_val, reason_text = row
                
                # Check candidate identification string schemas
                if not ID_REGEX.match(c_id):
                    issues_found.append(f"Line {line_number}: Format error on ID sequence '{c_id}'.")
                    
                if c_id in tracked_ids:
                    issues_found.append(f"Line {line_number}: Duplicate candidate key index record found for '{c_id}'.")
                tracked_ids.add(c_id)
                
                # Check line increment arrays match indices sequentially
                try:
                    rk = int(rank_val)
                    if rk != counter:
                        issues_found.append(f"Line {line_number}: Rank break index gap. Expected sequence index {counter}, got {rk}.")
                    if rk in tracked_ranks:
                        issues_found.append(f"Line {line_number}: Duplicate rank index assignment sequence value '{rk}'.")
                    tracked_ranks.add(rk)
                except ValueError:
                    issues_found.append(f"Line {line_number}: Non-integer value type allocation error for rank input sequence '{rank_val}'.")
                    
                # Score check type parsing validation
                try:
                    float(score_val)
                except ValueError:
                    issues_found.append(f"Line {line_number}: Floating data casting error for string score output metrics assignment reference '{score_val}'.")
                    
                # Verify non-empty justifications are mapped
                if not reason_text.strip():
                    issues_found.append(f"Line {line_number}: Blank evaluation metadata block row values found.")
                    
            if counter != TOTAL_ROWS_TARGET:
                issues_found.append(f"Record allocation length fault array error. Expected {TOTAL_ROWS_TARGET} row bounds, processed {counter}.")
                
    except Exception as error_msg:
        issues_found.append(f"File reading process failed unexpectedly: {error_msg}")
        
    return display_report(issues_found)

def display_report(logs):
    if logs:
        print("\n[FAILED] Structure verification checks yielded layout issues:")
        for bug in logs[:10]:
            print(f"  * {bug}")
        if len(logs) > 10:
            print(f"  ... (+ {len(logs) - 10} extra structural anomalies flagged).")
        return False
    else:
        print("\n" + "="*50)
        print("🎉 VALIDATION SUCCESS! YOUR SUBMISSION FILE IS PERFECT!")
        print("="*50)
        print("The file strictly satisfies all structural guidelines and is ready to upload.")
        return True

if __name__ == "__main__":
    # Scan environment paths recursively to target generated artifacts smoothly
    targets = [
        "submission.csv",
        "../submission.csv",
        "[PUB] India_runs_data_and_ai_challenge/submission.csv",
        "../[PUB] India_runs_data_and_ai_challenge/submission.csv"
    ]
    
    status = False
    for path_item in targets:
        if os.path.exists(path_item):
            if check_csv_formatting(path_item):
                status = True
                break
                
    if not status:
        print("\n[ERROR] Output artifact file path reference matrix targeted empty target scopes.")