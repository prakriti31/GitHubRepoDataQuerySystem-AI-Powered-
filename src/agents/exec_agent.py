import sys
import io
import matplotlib.pyplot as plt

class ExecAgent:
    """
    Executes Python code and captures outputs.
    """
    def run_code(self, code):
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        try:
            exec(code, {"plt": plt})
        except Exception as e:
            return f"Error executing code: {e}", None
        finally:
            sys.stdout = old_stdout
        return mystdout.getvalue(), plt
