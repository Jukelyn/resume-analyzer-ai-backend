"""
This module provides functionality to analyze resume texts using OpenAI's GPT
API.

It includes functions to:
- Chunk large text into manageable segments for processing.
- Analyze text using GPT-3.5-turbo, generating structured feedback for resume
evaluation.

Modules Imported:

- openai: For accessing the OpenAI API.
- config: For API key configuration.
- json: For parsing and validating JSON responses.
"""
import json
import openai
from config import Config

client = openai.OpenAI(api_key=Config.API_KEY)


def chunk_text(text: str, max_tokens: int = 4096) -> list[str]:
    """
    Split the given text into smaller chunks, ensuring each chunk is within the
    specified token limit.

    Args:
        text (str): The input text to be split.
        max_tokens (int, optional): The maximum token size per chunk.
                                    Defaults to 4096.

    Returns:
        (list[str]): A list of text chunks.
    """

    words = text.split()
    chunks = []
    while words:
        chunk = " ".join(words[:max_tokens])
        chunks.append(chunk)
        words = words[max_tokens:]
    return chunks


def analyze_text(user_text: str) -> dict:
    """
    Analyze the given resume text using GPT-3.5-turbo for structured feedback.

    Args:
        user_text (str): The resume text to be analyzed.

    Returns:
        (dict): A JSON response containing the analysis results.

    Raises:
        ValueError: If the API response is not a valid JSON object.
    """
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
        except json.JSONDecodeError as exc:
            raise ValueError("OpenAI did not return valid JSON.") from exc
        # This ensures that the json.JSONDecodeError is not supressed.

        results.append(structured_data)

    return results[0]
