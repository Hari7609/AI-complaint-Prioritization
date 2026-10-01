import json
from google import genai
from google.genai import types

def analyze_complaint(text: str) -> dict:
    """
    Uses Gemini to analyze complaint text, returning a JSON structure
    with category, priority, sentiment, and summary.
    """
    client = genai.Client() # Picks up GEMINI_API_KEY from environment variables
    
    prompt = f"""
    Analyze the following customer complaint and return a JSON object with these exact keys:
    - category (e.g., Billing, Technical, Customer Service, Product Defect)
    - priority (Low, Medium, High, Urgent)
    - sentiment (Positive, Neutral, Negative, Angry)
    - summary (A concise 1-sentence summary of the issue)

    Complaint: "{text}"
    """
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        # Fallback if API key is missing or network error occurs
        return {
            "category": "General",
            "priority": "Medium",
            "sentiment": "Neutral",
            "summary": f"Analysis failed: {str(e)}"
        }