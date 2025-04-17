from typing import List, Dict

SYSTEM_PROMPT = (
    "You are a career coach. Compare the resume text to the job description. "
    "Provide a JSON object with two keys: 'criteria' (list of {name, score_description}), and 'summary' (text summary)."
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
