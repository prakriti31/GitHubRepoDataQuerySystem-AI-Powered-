import sys
import io
import matplotlib.pyplot as plt

class ExecAgent:
    def run_code(self, code):
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            exec(code, {"plt": plt})
        except Exception as e:
            sys.stdout = old_stdout
            return f"Execution error: {e}", None

        sys.stdout = old_stdout
        return buffer.getvalue(), plt
