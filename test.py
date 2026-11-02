import sys
import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version


INPUT_LINES = """
django==4.2
numpy==2.3.0
scipy==1.7.0
scikit-learn==1.4.0
fastapi-agent-router==0.3.1
matplotlib==3.99.0
six==1.16.0
requests==2.32.0
""".strip().splitlines()


def evaluate_requirements(lines, target_py="3.11"):
    total_checked = 0
    not_found = 0
    incompatible = 0
    
    highest_pkg = None
    highest_min_version = None
    highest_req_str = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        total_checked += 1
        name, version = [part.strip() for part in line.split("==")]
        
        url = f"https://pypi.org/pypi/{name}/{version}/json"
        resp = requests.get(url)
        
        if resp.status_code == 404:
            not_found += 1
            continue
            
        data = resp.json()
        requires_python = data.get("info", {}).get("requires_python")
        
        if requires_python:
            spec = SpecifierSet(requires_python)
            if not spec.contains(target_py):
                incompatible += 1
                
            # Extract the minimum Python version requirement (e.g., from '>=3.10')
            # Specifiers typically look like ">=3.10", ">=3.8", "~=3.9"
            for s in spec:
                if s.operator in (">=", ">", "=="):
                    v = Version(s.version)
                    if highest_min_version is None or v > highest_min_version:
                        highest_min_version = v
                        highest_pkg = f"{name}=={version}"
                        highest_req_str = requires_python

    print(f"Dependencies checked: {total_checked}")
    print(f"Not found on PyPI: {not_found}")
    print(f"Incompatible with Python 3.11: {incompatible}")
    print(f"Highest requirement: {highest_pkg} ({highest_req_str})")

if __name__ == "__main__":
    evaluate_requirements(INPUT_LINES)