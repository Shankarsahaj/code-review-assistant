# llm_analyzer.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Default model (set in .env or fallback)
MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")

# Structured review prompt
PROMPT_TEMPLATE = """
You are a Senior Software Engineer performing a professional code review.

Review the following {language} code and provide your response in MARKDOWN format with these sections:

## SUMMARY
Brief summary of what the code does.

## ISSUES
Numbered list of issues found (severity: Critical/High/Medium/Low).

## SUGGESTIONS
Actionable improvements for each issue, include small code snippets.

## BEST PRACTICES
Mention naming, style, structure, and documentation improvements.

## SECURITY
Identify any potential security or input validation risks.

## OVERALL SCORE (1–10)
Give a rating and short reasoning.

Code to review:
```{language}
{code}
```
"""

# Perfect code generation prompt
PERFECT_CODE_TEMPLATE = """
You are a Senior Software Engineer. Based on the code review issues found, provide an improved version of the code that fixes all the problems.

Original {language} code:
```{language}
{code}
```

Provide ONLY the corrected code without any explanations. Make sure to:
- Fix all syntax errors
- Implement missing functionality
- Follow best practices
- Add proper error handling
- Include necessary imports
- Add meaningful comments

Return only the clean, working code:
"""

def analyze_code_with_llm(code_content: str, language: str = "python") -> dict:
    """Analyze code using Gemini and return both review and perfect code."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Get code review
        review_prompt = PROMPT_TEMPLATE.format(language=language, code=code_content)
        review_response = model.generate_content(review_prompt)
        
        # Get perfect code
        perfect_prompt = PERFECT_CODE_TEMPLATE.format(language=language, code=code_content)
        perfect_response = model.generate_content(perfect_prompt)
        
        # Extract responses
        review_text = ""
        perfect_code = ""
        
        if hasattr(review_response, "text") and review_response.text:
            review_text = review_response.text
        
        if hasattr(perfect_response, "text") and perfect_response.text:
            perfect_code = perfect_response.text
        
        return {
            "review_text": review_text,
            "perfect_code": perfect_code
        }

    except Exception as e:
        return {
            "review_text": f"❌ Error during analysis: {e}",
            "perfect_code": ""
        }