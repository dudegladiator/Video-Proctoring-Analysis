import numpy as np

# -----------------------------------------------------------------------------
# 1. Define activity levels for each distinct activity description.
#    (Higher numbers indicate higher suspicion.)
# -----------------------------------------------------------------------------
activity_levels = {
    # High Suspicion (Level 4)
    "Cell phone detected": 10,
    "Browser window swapped": 9,
    "Copy": 7,
    "Cut": 7,
    "Paste": 10,
    "Laptop detected": 10,
    "No face detected": 8,
    "Tab change detected": 8,
    "Window change detected": 8,
    
    # Medium-High Suspicion (Level 3)
    "Display change detected": 5,
    
    # Medium Suspicion (Level 2)
    "Window focus changed": 2,
    "Candidate looking left": 2,
    
    # Low Suspicion (Level 1)
    "Candidate looking right": 1,
    "Candidate looking down": 1,
    "Candidate looking up": 1,
    "Candidate iris looking left": 1,
    "Candidate iris looking right": 1,
}

# -----------------------------------------------------------------------------
# 2. Helper function: Convert timestamp "HH:MM:SS" to seconds.
#    If the timestamp contains "NaN", return np.nan.
# -----------------------------------------------------------------------------
def to_seconds(ts):
    if "NaN" in ts:
        return np.nan
    try:
        h, m, s = map(int, ts.split(":"))
        return h * 3600 + m * 60 + s
    except Exception:
        return np.nan

def analyze_algorithm_based_proctoring(log_data, scale=70):
    events = log_data
    if not events:
        return {
            "score": 0,
            "factor1": " NA",
            "factor2": " NA",
            "factor3": " NA"
        }
    
    weighted_scores = []
    timestamps = []
    breakdown = {}
    
    for event in events:
        desc = event.get("activityDescription", "").strip()
        count = event.get("count", 1)
        level = activity_levels.get(desc, 0)
        
        # Determine time multiplier: if event occurs in first 300 sec, multiply by 1.5
        ts = event.get("timeStampInVideo", event.get("timestampInVideo", "00:00:00"))
        sec = to_seconds(ts)
        timestamps.append(sec)
        multiplier = 1.5 if (sec is not None and not np.isnan(sec) and sec < 300) else 1.0
        
        contribution = level * count * multiplier
        weighted_scores.append(contribution)
        
        if level > 0:
            breakdown[desc] = breakdown.get(desc, 0) + contribution

    # Forward-fill any NaN timestamps with the last valid timestamp.
    clean_timestamps = []
    last_valid = 0
    for t in timestamps:
        if np.isnan(t):
            clean_timestamps.append(last_valid)
        else:
            clean_timestamps.append(t)
            last_valid = t

    raw_total = sum(weighted_scores)
    
    # Compute average time between events (in minutes)
    if len(clean_timestamps) > 1:
        diffs = np.diff(sorted(clean_timestamps))
        avg_diff = np.mean(diffs) / 60.0
    else:
        avg_diff = -1

    # Compute final score using hyperbolic transformation.
    try:
        final_score = 100 * (raw_total / (raw_total + scale))
    except Exception:
        final_score = 0

    # Determine top 3 contributing activities (using full activity names)
    sorted_breakdown = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    top3 = []
    for i in range(3):
        if i < len(sorted_breakdown):
            act, score_val = sorted_breakdown[i]
            top3.append(f"{act}:{score_val}")
        else:
            top3.append("NA")
    
    return {
        "score": round(final_score, 1),
        "factor1": top3[0],
        "factor2": top3[1],
        "factor3": top3[2]
    }


# if __name__ == "__main__":
#     # Read the input JSON file
#     input_file = "data/candidate37.json"
#     if not os.path.exists(input_file):
#         print(f"Error: Input file '{input_file}' not found.")
#         sys.exit(1)

#     with open(input_file, "r") as file:
#         input_data = json.load(file)

#     # Analyze the input data
#     output_data = analyze_log(input_data)

#     # Print the output data
#     print(json.dumps(output_data, indent=2))