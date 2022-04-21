#!/usr/bin/env python3

import re
import sys
from fnmatch import fnmatch

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

    version = name.split("/")[2]
    # visual representation of the regex: https://www.debuggex.com/r/u5mwGOGTowdfY4tO
    if not re.match(
        r"(?:tests|0\.0\.0|(?:[1-9][0-9]*\.(?:0|saas~[1-9][0-9]*)|saas~[1-9][0-9]+\.[1-9])(?:\.[0-9]+)+)", version
    ):
        print(
            f"❌ Invalid filename {name!r}. The version does match the expected pattern. "
            "See wiki: https://github.com/odoo/upgrade/wiki/How-To#where-to-write-upgrade-scripts"
        )
        rc = 1
        continue

sys.exit(rc)
