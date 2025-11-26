class SanitizeAgent:
    def clean_code(self, code):
        return code.replace("```python", "").replace("```", "").strip()
