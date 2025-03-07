import openai
from config import Config
import json

client = openai.OpenAI(api_key=Config.API_KEY)

def chunk_text(text, max_tokens=4096):
    words = text.split()
    chunks = []
    while words:
        chunk = " ".join(words[:max_tokens])
        chunks.append(chunk)
        words = words[max_tokens:]
    return chunks

def analyze_text(user_text):
    text_chunks = chunk_text(user_text, max_tokens=4096)

    results = []
    for chunk in text_chunks:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[{
                    "role": "system",
                    "content": (
                        "You are an expert career coach and resume evaluator. "
                        "Analyze the provided resume and return a structured JSON response with the following keys:\n"
                        "- `resume_score` (integer from 0-100)\n"
                        "- `things_done_well` (list of 6 one to two word bullet points (e.g. Experience Level))\n"
                        "- `areas_for_improvement` (list of 6 one to two word bullet points (e.g. Clarity ))\n"
                        "- `full_analysis` (detailed Markdown breakdown with strengths, weaknesses, and actionable suggestions. Add any extra insights outside of the 6 listed points.)"
                        "- `summary` (summary of the analysis. Do not refer to the resume owner by name)"
                        "Create a summary of your analysis and put it before the Strengths, Areas for improvement, and Additional Suggestions"
                        "Ensure the response is valid JSON with no extra text before or after the JSON object."
                        "Do not include a header in the full_analysis"
                        "Add a line break in between Strengths, Areas for improvement, and Additional Suggestions"

                    "### Formatting Instructions:\n"
                    "1. The `full_analysis` section should be formatted using Markdown.\n"
                    "2. **Use '### Strengths', '### Areas for Improvement', and '### Additional Suggestions' as section headers.**\n"
                    "3. Add a blank line (`\\n\\n`) between each section for readability.\n"
                    ),
                },
            {"role": "user", "content": chunk}],
            temperature=0.2
        )
        json_response = response.choices[0].message.content

        try:
            structured_data = json.loads(json_response)
        except json.JSONDecodeError:
         raise ValueError("OpenAI did not return valid JSON.")

        results.append(structured_data)

    return results[0]
