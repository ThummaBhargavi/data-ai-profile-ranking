import os
import json
import csv

def load_data():
    # Check current directory and subdirectories for data files
    targets = ["candidates.jsonl", "sample_candidates.json"]
    
    # Simple search loop over possible file locations
    for path in targets:
        if os.path.exists(path):
            print(f"--> Found dataset file: {path}")
            return parse_file(path)
            
    # Deep walk through workspace folders as a fallback if paths are nested
    for root, _, files in os.walk("."):
        if "_MACOSX" in root: 
            continue
        for f in files:
            if f in targets:
                target_path = os.path.join(root, f)
                print(f"--> Deep scan located file at: {target_path}")
                return parse_file(target_path)
                
    raise FileNotFoundError("Dataset files missing from current directories.")

def parse_file(filepath):
    # Split handling for streaming JSONL format vs standard JSON arrays
    if filepath.endswith(".jsonl"):
        data = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

def evaluate_and_rank(raw_records):
    processed_results = []
    
    # List of classic IT service firms to check for background filters
    top_it_firms = ["tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "tech mahindra", "hcl"]

    for row in raw_records:
        c_id = row.get("candidate_id", "UNKNOWN")
        prof = row.get("profile", {})
        
        # Pull profile features
        job_title = prof.get("current_title", "").lower()
        yoe = prof.get("years_of_experience", 0)
        skills_list = [s.lower() for s in prof.get("skills", [])]
        history = prof.get("work_history", [])
        
        # Activity markers
        metrics = row.get("redrob_signals", {})
        idle_months = metrics.get("months_since_last_login", 12)
        reply_rate = metrics.get("recruiter_response_rate", 0.0)
        
        # Base confidence initialization
        score = 0.5
        notes = []
        
        # Metric 1: Experience mapping
        if 5 <= yoe <= 9:
            score += 0.25
            notes.append(f"Ideal senior experience profile ({yoe} years)")
        elif 10 <= yoe <= 12:
            score += 0.15
            notes.append(f"Highly experienced profile ({yoe} years)")
        elif yoe < 4:
            score -= 0.35
            notes.append(f"Insufficient experience ({yoe} years)")
            
        # Metric 2: Core domain keyword triggers
        ai_keywords = ["ai", "machine learning", "ml", "nlp", "llm", "deep learning"]
        if any(kw in job_title for kw in ai_keywords):
            score += 0.2
            notes.append("Strong technical title alignment in AI/ML")
        elif "engineer" in job_title or "developer" in job_title:
            score += 0.05
            notes.append("Core engineering background match")

        # Metric 3: Verify engineering history benchmarks
        from_service_background = False
        for position in history:
            comp = position.get("company_name", "").lower()
            if any(firm in comp for firm in top_it_firms):
                from_service_background = True
                break
        
        if from_service_background:
            score -= 0.25
            notes.append("Down-ranked due to service/consulting firm background")

        # Metric 4: Integrity / Anomaly outlier flags
        if (len(skills_list) > 15 and yoe <= 1) or (len(history) > 4 and yoe <= 1):
            score -= 0.55
            notes.append("Flagged profile anomaly with impossible ratios")

        # Metric 5: Platform interaction activity levels
        if idle_months <= 2:
            score += 0.1
        elif idle_months > 6:
            score -= 0.15
            
        if reply_rate >= 0.8:
            score += 0.05
            
        # Compile reasoning summaries
        compiled_notes = "; ".join(notes)[:200]
        if not compiled_notes:
            compiled_notes = "Profile matches core structural metrics."
            
        processed_results.append({
            "candidate_id": c_id,
            "score": round(score, 4),
            "reasoning": compiled_notes
        })
        
    # Sort descending by score, resolve ties deterministically using ID strings
    processed_results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    output_subset = processed_results[:100]
    
    # Inline tracking index assignment
    for index, item in enumerate(output_subset):
        item["rank"] = index + 1
        
    return output_subset

def write_results(dataset):
    headers = ["candidate_id", "rank", "score", "reasoning"]
    
    # Save destinations across directory boundaries
    export_paths = [
        "submission.csv",
        "[PUB] India_runs_data_and_ai_challenge/submission.csv",
        "India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/submission.csv"
    ]
    
    for path in export_paths:
        try:
            base_dir = os.path.dirname(path)
            if base_dir and not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
                
            with open(path, "w", newline="", encoding="utf-8") as out_file:
                obj = csv.DictWriter(out_file, fieldnames=headers)
                obj.writeheader()
                for record in dataset:
                    obj.writerow(record)
            print(f"[SUCCESS] Exported submission to: {path}")
        except Exception:
            continue

if __name__ == "__main__":
    try:
        loaded_candidates = load_data()
        ranked_metrics = evaluate_and_rank(loaded_candidates)
        write_results(ranked_metrics)
        print("\n--- Pipeline finished successfully ---")
    except Exception as err:
        print(f"\nExecution terminated with error: {err}")