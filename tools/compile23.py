#!/usr/bin/env python3
# ruff: noqa: T201
import subprocess
import sys
from pathlib import PurePath

py2_only_patterns = [
    "migrations/*/[789].0.*/*.py",
    "migrations/*/[789].saas~*.*/*.py",
    "migrations/*/10.0.*/*.py",
]
py2_files = []

py3_only_patterns = [
    "tools/*.py",
    # tests are only run from version 12. python2 compatibility is not needed.
    "migrations/*/tests/*.py",
    "migrations/*/10.saas~1[45678].*/*.py",  # upgrade from 10 to 11 is done using python3
    "migrations/*/1[123456789].0.*/*.py",
    "migrations/*/saas~1[123456789].[123456789].*/*.py",
]
py3_files = []

rc = 0

for filename in sys.argv[1:]:
    p = PurePath(filename)
    if p.suffix != ".py":
        continue

    if not filename.islower():
        print(f"filename {filename!r} is not lowercase")
        rc = 1

    if any(p.match(pattern) for pattern in py2_only_patterns):
        py2_files.append(filename)
    elif any(p.match(pattern) for pattern in py3_only_patterns):
        py3_files.append(filename)
    else:
        # not an explicit match to a python version. Test against both versions.
        py2_files.append(filename)
        py3_files.append(filename)


if py2_files:
    s = subprocess.run(["python2", "-m", "compileall", "-f", "-q", *py2_files], check=False)
    if s.returncode:
        rc = 1

if py3_files:
    s = subprocess.run(["python3", "-m", "compileall", "-f", "-q", *py3_files], check=False)
    if s.returncode:
        rc = 1

sys.exit(rc)
