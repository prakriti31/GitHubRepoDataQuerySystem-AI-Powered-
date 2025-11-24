import sys

print("🔍 PHASE 1 ENVIRONMENT CHECK")

print(f"Using Python version: {sys.version}")

required_packages = [
    "requests",
    "pandas",
    "psycopg2",
    "sqlalchemy",
    "streamlit",
    "langchain",
    "plotly",
    "prophet",
    "statsmodels"
]

print("\nChecking installed packages...\n")

missing = []

for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"✔ {pkg} OK")
    except ImportError:
        print(f"✘ {pkg} NOT INSTALLED")
        missing.append(pkg)

if len(missing) == 0:
    print("\n🎉 All required packages installed!")
else:
    print("\n⚠ Missing packages:")
    for m in missing:
        print(" -", m)
    print("\nInstall by running:")
    print("uv pip install -r requirements.txt")
