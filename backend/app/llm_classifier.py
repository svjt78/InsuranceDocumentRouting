import openai
import json
from .config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def classify_document(extracted_text: str) -> dict:
    prompt = f"""
You are an insurance document classifier. Given the document text below, determine:
1. The Department (one of 7, e.g., Claims, Policy Management, Underwriting, etc.)
2. The Category (e.g., Policy Application, Claim Filing, Renewal, etc.)
3. The Subcategory (e.g., New Application, Renewal Notice, Endorsement, etc.)
4. A bullet-point summary of key points.
5. A checklist of recommended action items.

Return a valid JSON object with keys "department", "category", "subcategory", "summary", and "action_items".

Document Text:
\"\"\"{extracted_text}\"\"\"
    """
    try:
      #  response = openai.ChatCompletion.create(
      #      model="gpt-3.5-turbo",
      #      messages=[
      #          {"role": "system", "content": "You are an expert document classifier."},
      #          {"role": "user", "content": prompt}
      #      ],
      #      temperature=0.0
      #  )
        result_text = response.choices[0].message['content']
        result = json.loads(result_text)
        return result
    except Exception as e:
        print(f"LLM classification error: {e}")
        return {}
