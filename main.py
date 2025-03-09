import asyncio
import json
from time import sleep

from algorithm_analyzer import analyze_algorithm_based_proctoring
from llm_analyzer import analyze_proctoring_log
from ml_analyzer import analyze_ml_based_proctoring
from util import get_score_color, get_score_status

def main_output(candidate_data, activity_log):
    try:
        ai_based_proctoring = asyncio.run(analyze_proctoring_log(activity_log))
        algorithm_based_proctoring = analyze_algorithm_based_proctoring(activity_log)
        ml_based_proctoring = analyze_ml_based_proctoring(activity_log)
        
        if ml_based_proctoring.get('score', 0) > 0:
            final_score = 0.3 * algorithm_based_proctoring.get('score', 0) + 0.45 * ai_based_proctoring.get('score', 0) + 0.25 * ml_based_proctoring.get('score', 0)
        else:
            final_score = 0.4 * algorithm_based_proctoring.get('score', 0) + 0.6 * ai_based_proctoring.get('score', 0)
        return {
            "id": candidate_data.get('id'),
            "name": candidate_data.get('name', 'Unknown Candidate'),
            "status": get_score_status(final_score),
            "color": get_score_color(final_score),
            "overall_score": round(final_score, 2),  # Upto two digits
            "overall_analysis": ai_based_proctoring.get('analysis', 'No analysis available'),
            "exam_name": candidate_data.get('exam_name', 'Unknown Exam'),
            "exam_date": candidate_data.get('exam_date', '2025-03-09'),
            "ai_based_proctoring": ai_based_proctoring,
            "algorithm_based_proctoring": algorithm_based_proctoring,
            "ml_based_proctoring": ml_based_proctoring
        }
    except Exception as e: 
        print(f"Error analyzing proctoring: {e}")
        ai_based_proctoring = {
            'score': 0,
            'analysis': 'No analysis available'
        }
        algorithm_based_proctoring = {
            'score': 0,
            'factor1': 'No factors available',
            'factor2': 'No factors available',
            'factor3': 'No factors available'
        }
        ml_based_proctoring = {
            'score': 0
        }
        return {
            "id": candidate_data.get('id'),
            "name": candidate_data.get('name', 'Unknown Candidate'),
            "status": get_score_status(0),
            "color": get_score_color(0),
            "overall_score": 0,
            "overall_analysis": 'No analysis available',
            "exam_name": candidate_data.get('exam_name', 'Unknown Exam'),
            "exam_date": candidate_data.get('exam_date', '2025-03-09'),
            "ai_based_proctoring": ai_based_proctoring,
            "algorithm_based_proctoring": algorithm_based_proctoring,
            "ml_based_proctoring": ml_based_proctoring
        }

def load_candidates():
    try:
        with open('processed_candidates.json', 'r') as file:
            candidates = json.load(file)
        
        processed_candidates = []
        for candidate in candidates:
            processed_candidates.append({
                "id": candidate.get('id'),
                "name": candidate.get('name', 'Unknown Candidate'),
                "score": candidate.get('score', 0),
                "status": candidate.get('status', 'Unknown Status'),
                "color": get_score_color(candidate.get('score', 0)),
                "overall_score": candidate.get('overall_score', 0),
                "overall_analysis": candidate.get('overall_analysis', ''),
                "exam_name": candidate.get('exam_name', 'Unknown Exam'),
                "exam_date": candidate.get('exam_date', '2025-03-09'),
                "ai_based_proctoring": candidate.get('ai_based_proctoring', {
                    'score': 20,
                    'analysis': 'No analysis available'
                }),
                "algorithm_based_proctoring": candidate.get('algorithm_based_proctoring', {
                    'score': 0,
                    'factor1': 'No factors available',
                    'factor2': 'No factors available',
                    'factor3': 'No factors available'
                }),
                "ml_based_proctoring": candidate.get('ml_based_proctoring', {
                    'score': 0
                })
            })
        return processed_candidates
    except Exception as e:
        print(f"Error loading candidates.json: {e}")
        return []
    
def load_activity_log(candidate_id):
    """Load real activity log from data directory"""
    try:
        file_path = f"data/candidate{candidate_id}.json"
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        # Extract activity log from the loaded data
        activity_log = data.get('activityLog', [])
        
        # Ensure each log entry has required fields
        processed_logs = []
        for log in activity_log:
            processed_logs.append({
                "type": log.get("type", "Extension Proctoring"),
                "timeStampInVideo": log.get("timeStampInVideo", "00:00:00"),
                "activityDescription": log.get("activityDescription", "Unknown"),
                "count": log.get("count", 1)
            })
            
        return processed_logs
    except FileNotFoundError:
        print(f"Activity log file not found for candidate {candidate_id}")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON in activity log file for candidate {candidate_id}")
        return []
    except Exception as e:
        print(f"Error loading activity log for candidate {candidate_id}: {e}")
        return []
    
if __name__ == "__main__":
    # Load candidates from candidates.json
    candidates = []
    try:
        with open('candidates.json', 'r') as file:
            candidates = json.load(file)
    except Exception as e:
        print(f"Error loading candidates.json: {e}")
        candidates = []

    # Load ML scores
    ml_scores = {}
    try:
        with open('ml_based_proctoring.json', 'r') as file:
            ml_data = json.load(file)
            ml_scores = {item['id']: item['score'] for item in ml_data['candidates']}
    except Exception as e:
        print(f"Error loading ml_scores.json: {e}")
        ml_scores = {}

    # Process each candidate and store results
    results = []
    for candidate in candidates:
        try:
            candidate_id = candidate['id']
            
            # Load activity log for the candidate
            activity_log = load_activity_log(candidate_id)

            # Process candidate data through main_output
            result = main_output(candidate, activity_log)
            
            result["ml_based_proctoring"]["score"] = ml_scores.get(candidate_id, 0)
            
            results.append(result)
            
            print(f"Processed candidate {candidate_id}: {candidate.get('name', 'Unknown')}")
            print(result)
            sleep(60)  # Sleep for 1 second to avoid rate limiting
        except Exception as e:
            print(f"Error processing candidate {candidate.get('id')}: {e}")
            continue

    # Save results to output file
    try:
        output_file = 'processed_candidates.json'
        with open(output_file, 'w') as file:
            json.dump(results, file, indent=2)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")