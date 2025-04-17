from typing import List, Dict

SYSTEM_PROMPT = (
    "You are a career coach. Compare a candidate's resume against the job description. "
    "Return only a single JSON object with exactly two keys: 'criteria' (list of {name: string, score_description: string}) "
    "and 'summary' (a concise summary of how the resume matches). Do not include markdown, explanations, or code fences."
)

def get_compare_messages(jd_content: str, resume_text: str) -> List[Dict[str, str]]:
    """
    Build the messages payload for OpenAI ChatCompletion compare endpoint.
    """
    user_prompt = f"Job Description:\n{jd_content}\n\nResume Text:\n{resume_text}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
