#!/usr/bin/env python3

import ast
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).parent.parent

rc = 0
for name in sys.argv[1:]:
    if not name.startswith("migrations/"):
        continue

    if (
        name in {"migrations/__init__.py", "migrations/testing.py"}
        or fnmatch(name, "migrations/util/*")
        or fnmatch(name, "migrations/_lib2to3_fixers/*.py")
    ):
        continue

    if not fnmatch(name, "migrations/*/*/*.*"):
        print(
            f"❌ Invalid filename {name!r}. Upgrade scripts should have the pattern `$module/$version/{{pre,post,end}}-$name.py`"
        )
        rc = 1
        continue

    path = Path(name)
    version = path.parts[2]

    if version == "tests":
        # verify that tests are imported
        if path.name == "__init__.py":
            continue

        if not fnmatch(path.name, "test_*.py"):
            print(f"❌ Invalid test filename {name!r}. Test files should start with `test_`.")
            rc = 1
            continue

        init = ROOT / path.parent / "__init__.py"
        if not init.exists():
            print(f"❌ Missing init file `{init.relative_to(ROOT)!s}`. It should import {path.stem!r}.")
            rc = 1
            continue

        for node in ast.walk(ast.parse(init.read_text())):
            if isinstance(node, ast.alias) and node.name == path.stem:
                break
        else:
            print(f"❌ The test file {name!r} is not imported in the `__init__.py` file.")
            rc = 1
            continue

    elif not re.match(
        r"(?:0\.0\.0|(?:[1-9][0-9]*\.(?:0|saas~[1-9][0-9]*)|saas~[1-9][0-9]+\.[1-9])(?:\.[0-9]+)+)", version
    ):
        # visual representation of the regex: https://www.debuggex.com/r/u5mwGOGTowdfY4tO (minus the `tests` part)
        print(
            f"❌ Invalid filename {name!r}. The version does match the expected pattern. "
            "See wiki: https://github.com/odoo/upgrade/wiki/How-To#where-to-write-upgrade-scripts"
        )
        rc = 1
        continue

sys.exit(rc)
