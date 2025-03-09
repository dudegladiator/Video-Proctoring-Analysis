import asyncio
import glob
import json
import os
from fastapi import HTTPException
from typing import Dict, List, Any, Optional

from llm_tool import google_chat_completions, groq_chat_completions, mistral_chat_completions

def create_system_prompt():
    return """
You are an expert online exam proctor analyzing activity logs to determine if a student is cheating.

The logs contain timestamps and activities detected during an online exam. Your task is to analyze this data and determine the probability of cheating on a scale from 0-100.

Activity Classification and Significance:

HIGH SUSPICION Activities:
- Browser window swapped
- Cell phone detected
- Copy/Cut/Paste actions
- Tab change detected
- Window change detected
- Laptop detected (secondary device)
- No face detected

NORMAL Behavioral Activities (Low Suspicion):
- Candidate looking right (MOST COMMON, NORMAL)
- Candidate looking down (normal for typing/writing)
- Candidate looking up (occasional thinking)
- Window focus changed (if isolated incidents)

Important Human Behavioral Context:
1. Looking Patterns:
   - Right-looking is NORMAL because:
     * Most people are right-handed
     * Natural writing/typing position
     * Note-taking behavior
     * Normal cognitive processing
   - Down-looking is NORMAL for:
     * Typing
     * Writing notes
     * Reading questions
   - Up-looking is NORMAL for:
     * Thinking/recall
     * Mental calculations
     * Problem-solving

2. Time-Based Context:
   First 5 minutes (300 seconds):
   - Higher activity is normal due to:
     * Setup and adjustment
     * Initial nervousness
     * System familiarization
   
   Last 5 minutes (300 seconds):
   - Increased activity is expected for:
     * Submission process
     * Final review
     * Time pressure activities

Suspicious Patterns to Focus On:
1. Multiple HIGH SUSPICION activities outside first/last 5 minutes
2. Clusters of window/browser changes
3. Copy/Paste actions combined with window changes
4. Cell phone or second device detection
5. Extended periods of no face detection

Normal Patterns to Ignore:
1. Regular right/down looking patterns
2. Isolated window focus changes
3. Brief up-looking for thinking
4. Activity spikes in first/last 5 minutes
5. Scattered, non-clustered looking patterns

Your response must be a valid JSON with:
- "score": Integer from 0-100 (0=definitely not cheating, 100=definitely cheating)
- "analysis": Brief explanation of your reasoning (5-10 sentences)

Scoring Guidelines:
- Start from a baseline of 0
- Add points for:
  * HIGH SUSPICION activities (especially in clusters)
  * Combined suspicious patterns
  * Systematic switching behavior
- Ignore or minimize:
  * Normal looking patterns
  * First/last 5-minute activities
  * Isolated window focus changes
  * Natural eye movements

Focus on identifying patterns that clearly deviate from normal test-taking behavior while accounting for natural human behaviors and time-based contexts.
"""

def format_activity_log(activity_log):
    """Format the activity log for better analysis by including derived metrics"""
    # Convert timestamps to seconds for temporal analysis
    events_with_seconds = []
    for entry in activity_log:
        ts = entry.get("timeStampInVideo", "")
        desc = entry.get("activityDescription", "")
        count = entry.get("count", 1)
        
        seconds = None
        if ts != "NaN:NaN:NaN" and ":" in ts:
            try:
                h, m, s = map(int, ts.split(":"))
                seconds = h*3600 + m*60 + s
            except:
                pass
                
        events_with_seconds.append({
            "timestamp": ts,
            "seconds": seconds,
            "description": desc,
            "count": count
        })
    
    # Calculate time intervals between events
    intervals = []
    for i in range(1, len(events_with_seconds)):
        if events_with_seconds[i]["seconds"] is not None and events_with_seconds[i-1]["seconds"] is not None:
            interval = events_with_seconds[i]["seconds"] - events_with_seconds[i-1]["seconds"]
            intervals.append(interval)
    
    # Count activity types
    activity_counts = {}
    for event in activity_log:
        desc = event.get("activityDescription", "")
        count = event.get("count", 1)
        if desc in activity_counts:
            activity_counts[desc] += count
        else:
            activity_counts[desc] = count
    
    return {
        "raw_log": activity_log,
        "events_with_seconds": events_with_seconds,
        "intervals": intervals,
        "activity_counts": activity_counts
    }

def create_input_prompt(formatted_log):
    """Creates a detailed prompt for the LLM analysis"""
    raw_log = json.dumps(formatted_log["raw_log"], indent=2)
    
    # Calculate statistics
    total_events = sum(formatted_log["activity_counts"].values())
    avg_interval = sum(formatted_log["intervals"]) / len(formatted_log["intervals"]) if formatted_log["intervals"] else 0
    
    # Format and return the prompt
    return f"""
Please analyze this proctoring activity log to detect potential cheating:

{raw_log}

Statistics:
- Total events: {total_events}
- Activity counts: {formatted_log["activity_counts"]}
- Time intervals between events (seconds): {formatted_log["intervals"]}
- Average interval: {avg_interval:.1f} seconds

Based on the log content and these statistics, determine the likelihood of cheating.
Consider the number, timing, and patterns of window changes and focus changes, paying particular attention to activity *outside* the first 300 seconds (5 minutes) and the last 300 seconds of the exam.
Remember that "looking right" is generally normal behavior and should only be considered suspicious if combined with other indicators.
Return your analysis in the required JSON format with 'score' and 'analysis' fields.
"""

async def process_llm_responses(responses):
    """
    Processes responses from multiple LLMs and uses a final LLM call 
    to synthesize the most accurate analysis
    """
    valid_responses = []
    
    # Validate and collect responses from all models
    for response in responses:
        if isinstance(response, str):
            try:
                parsed = json.loads(response)
                if isinstance(parsed, dict) and "score" in parsed and "analysis" in parsed:
                    valid_responses.append(parsed)
            except:
                continue
    
    if not valid_responses:
        return {
            "score": 0,
            "analysis": "Error: Unable to analyze proctoring log with any LLM."
        }
        
    # for r in valid_responses:
    #     print(f"Model : Score = {r['score']}, Analysis = \"{r['analysis']}\"")
    
    # Calculate initial average score
    total_score = sum(r["score"] for r in valid_responses)
    avg_score = round(total_score / len(valid_responses))
    
    # Format all previous analyses for meta-review
    model_analyses = "\n".join([
        f"Model {i+1}: Score = {r['score']}, Analysis = \"{r['analysis']}\""
        for i, r in enumerate(valid_responses)
    ])
    
    # Create a prompt for the final analysis
    final_analysis_prompt = f"""
Review these analyses of an exam proctoring activity log from multiple AI models:

{model_analyses}

Your task is to synthesize these analyses into a single definitive assessment.
Consider:
1. Common patterns identified across multiple models
2. Any unique insights from individual models
3. The overall consensus on suspicious activity
4. The distribution of scores ({[r['score'] for r in valid_responses]})
5. The temporal patterns in the raw log

Return ONLY a JSON object with:
1. "analysis": A brief (2-3 sentences) final analysis that captures the most important insights
2. "score": A refined final score from 0-100
"""

    # System prompt for final analysis
    system_prompt = """
You are a meta-analyzer of AI proctoring assessments. Your task is to synthesize multiple AI analyses 
into a single coherent and accurate assessment. Focus on identifying the most reliable signals of 
potential cheating across all models while eliminating false positives.

Return only a valid JSON with an "analysis" field (1-2 sentences) and a "score" field (integer 0-100).
"""

    try:
        # Call the final LLM (using Google's model which excels at synthesis tasks)
        final_response = await google_chat_completions(
            input=final_analysis_prompt,
            system_prompt=system_prompt,
            model="gemini-2.0-flash-thinking-exp-01-21"
        )
        
        # Parse and return the final synthesized analysis
        final_result = json.loads(final_response)
        return {
            "score": final_result.get("score", avg_score),
            "analysis": final_result.get("analysis", "Unable to generate final analysis")
        }
    except Exception as e:
        # Fallback to highest-score analysis if meta-analysis fails
        primary_analysis = max(valid_responses, key=lambda x: x["score"])["analysis"]
        return {
            "score": avg_score,
            "analysis": primary_analysis
        }

async def analyze_proctoring_log(activity_log: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes proctoring logs using multiple LLMs and combines their assessments
    for more reliable cheating detection.
    
    Args:
        activity_log: List of dictionaries with proctoring events
        
    Returns:
        Dictionary with analysis and score
    """
    # Format the activity log for easier analysis
    formatted_log = format_activity_log(activity_log)
    
    # Create enhanced system prompt
    system_prompt = create_system_prompt()
    
    # Create the input prompt with formatted log and analysis instructions
    input_prompt = create_input_prompt(formatted_log)
    # Get predictions from all three LLM services concurrently
    tasks = [
        google_chat_completions(input_prompt, system_prompt),
        # groq_chat_completions(input_prompt, system_prompt),
        mistral_chat_completions(input_prompt, system_prompt)
    ]
    
    # Wait for all responses
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process valid responses and combine results
    result = await process_llm_responses(responses)
    return result

# Example usage
# if __name__ == "__main__":
#     # Get all JSON files matching the pattern "candidate*.json" in the "data" directory
#     json_file = "data/candidate37.json"
    
#     try:
#         # Open and read the JSON file
#         with open(json_file, 'r', encoding='utf-8') as file:
#             # Load JSON content into a Python dictionary
#             activity_log = json.load(file)
            
#             # Process the activity log (assuming llm_analyzer is defined elsewhere)
#             result = asyncio.run(analyze_proctoring_log(activity_log.get("activityLog", [])))
            
#             # Print the results
#             print(json.dumps(result, indent=2))
            
#     except FileNotFoundError:
#         print(f"Error: File {json_file} not found")
#     except json.JSONDecodeError:
#         print(f"Error: Invalid JSON format in {json_file}")
#     except Exception as e:
#         print(f"Error processing {json_file}: {str(e)}")