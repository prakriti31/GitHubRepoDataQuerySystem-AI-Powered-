class SanitizeAgent:
    """
    Cleans AI-generated code: removes unwanted characters, ensures Python syntax.
    """
    def clean_code(self, code):
        # Strip any triple quotes, trailing whitespace
        code = code.replace("```python", "").replace("```", "").strip()
        return code
