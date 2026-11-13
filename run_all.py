"""Rebuild every synthetic case study result, stopping on the first failure."""
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parent
for app in sorted((root/'projects').glob('*/app.py')):
    result=subprocess.run([sys.executable,str(app)],capture_output=True,text=True)
    if result.returncode:
        print(result.stderr,file=sys.stderr)
        raise SystemExit(result.returncode)
    print(f'OK {app.parent.name}')
