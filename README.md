# Segment 4 Repository

## Quick Links
- [Live Dashboard Demo](https://video-proctoring-analysis.streamlit.app/)
- [Project Drive Folder](https://drive.google.com/drive/folders/1OsAnu-ICVHgi_HD5QZaEKf-N4C941W4r?usp=sharing)

## Dashboard Setup Instructions

### Prerequisites
- Python installed on your system
- pip package manager

### Installation Steps

1. **Create Python Environment**
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate virtual environment
   # For Windows:
   venv\Scripts\activate
   # For Unix/MacOS:
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dashboard**
   ```bash
   streamlit run app.py
   ```

## Analysis Methodology

Our proctoring system utilizes a triple-layer validation approach, combining multiple analytical methodologies for comprehensive cheating detection with high accuracy and minimal false positives.

### Three-Tier Analysis Architecture

#### 1. LLM Analysis
- Leverages advanced large language models (Gemini, Mistral)
- Contextually analyzes suspicious behaviors
- Provides human-readable explanations for detected anomalies
- Excels at identifying sophisticated cheating patterns

#### 2. Algorithm Analysis
- Rule-based system with empirically-derived heuristics
- Contextual awareness of exam phases
- Real-time suspicion score calculation
- Efficient detection with low computational overhead

#### 3. Machine Learning Analysis
- Trained on verified cheating/non-cheating behaviors
- Identifies subtle behavioral patterns
- Reduces false positives through contextual learning
- Continuous improvement through feedback mechanisms

The system combines outputs from all three tiers to provide comprehensive risk assessment, leveraging each method's strengths while mitigating individual limitations.