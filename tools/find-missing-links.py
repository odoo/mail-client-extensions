#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///

# ruff: noqa: PLW0603, T201

import ast
import sys
from argparse import ArgumentParser
from pathlib import Path

VERBOSE = False
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

EXCEPTIONS = {
    MIGRATIONS_DIR / e
    for e in (
        # scripts that don't need a symlink because they are already handled in other ways
        "report/10.saas~14.1.0/pre-migrate.py",
        "website_account/10.saas~17.1.0/pre-migrate.py",
        "website_subscription/10.saas~17.1.0/pre-01-payment.py",
        "website_subscription/10.saas~17.1.0/pre-migrate.py",
        "account_followup/8.saas~6.1.0/pre-10-rename-xid.py",
        # explicitly called (util.import_script)
        "sale_payment/saas~11.4.1.0/pre-migrate.py",
        "sale_order_dates/saas~11.4.1.1/pre-migrate.py",
        # views also removed
        "google_base_account/7.saas~2.1.0/pre-10-remove-views.py",
        "account_analytic_analysis/8.saas~6.1.1/pre-rm-views.py",
        "account_invoicing/saas~11.1.1.0/pre-remove.py",
    )
}


def saas(x, y):
    """inject `saas~` in the right place depending of the major version"""
    if x >= 11:
        return f"saas~{x}.{y}"
    return f"{x}.saas~{y}"


def previous_versions(version):
    """
    returns glob-aware wildcard matches for previous versions
    of given versions up to previous major version
    """
    v = list(map(int, version.replace("saas~", "").split(".")))

    if v[1] == 0:
        matches = [saas(v[0] - 1, "*")]
    else:
        min_saas = {8: 6, 9: 7, 10: 14}
        matches = [saas(v[0], f"{m}.*") for m in range(min_saas.get(v[0], 1), v[1])]

    return [*matches, f"{version}.*"]


def _match_linked_files(version, new, found, reason):
    result = True
    expected = {f for f in found.iterdir() if f.is_file()}

    for exc in expected & EXCEPTIONS:
        exc = exc.relative_to(MIGRATIONS_DIR)  # noqa: PLW2901
        if VERBOSE:
            print(f"🆗 {exc} manually handled in {new}/{version} ▶︎ [module {reason}]")

    expected -= EXCEPTIONS
    if not expected:
        return True

    target_links = {
        str(g.relative_to(MIGRATIONS_DIR)): g.resolve()
        for g in MIGRATIONS_DIR.glob(f"{new}/{version}.*/*")
        if g.is_symlink()
    }
    missing = expected - set(target_links.values())
    if not missing:
        for link, target in target_links.items():
            if target in expected:
                ltarget = target.relative_to(MIGRATIONS_DIR)
                if VERBOSE:
                    print(f"✅ {link} -> {ltarget} ▶︎ [{reason} in {version}]")
    else:
        result = False
        link = f"{new}/{version}.???"
        for script in missing:
            lscript = script.relative_to(MIGRATIONS_DIR)
            bscript = lscript.name
            print(f"❌ MISSING SYMLINK: {link}/{bscript} -> {lscript} ▶︎ [{reason} in {version}]")

    return result


def check_module_rename(version, old, new):
    result = True

    for match in previous_versions(version):
        for found in MIGRATIONS_DIR.glob(f"{old}/{match}"):
            old_script_version = found.name
            maybe_link = MIGRATIONS_DIR / new / old_script_version

            lfound = found.relative_to(MIGRATIONS_DIR)
            link = maybe_link.relative_to(MIGRATIONS_DIR)

            if maybe_link.is_symlink():
                if maybe_link.samefile(found):
                    if VERBOSE:
                        print(f"✅ {link} -> {lfound} ▶︎ [renamed in {version}]")
                else:
                    result = False
                    print(f"💥 INVALID SYMLINK: {link} -/-> {lfound} ▶︎ [renamed in {version}]")
            elif maybe_link.is_dir():
                result = False
                print(
                    f"❗ DUPLICATED SCRIPTS: {link} is a real folder; "
                    f"expected symlink to {lfound} ▶︎ [renamed in {version}]"
                )
            elif not _match_linked_files(version, new, found, "renamed"):
                result = False
                print(f"❌ MISSING SYMLINK: {link} -> {lfound} ▶︎ [renamed in {version}]")
    return result


def check_module_merge(version, old, new):
    result = True

    for match in previous_versions(version):
        for found in MIGRATIONS_DIR.glob(f"{old}/{match}"):
            # In case of module merge, we need to track files instead of directories
            # Even if file is symlinked, scripts should be written defensively because
            # table and columns may not exists.
            # XMLIDs should also be named differently based on running version.
            result = _match_linked_files(version, new, found, "merged") and result

    return result


def main():
    global VERBOSE
    rc = 0

    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    options = parser.parse_args()
    VERBOSE = options.verbose

    for pyfile in MIGRATIONS_DIR.glob("base/*/*.py"):
        version = pyfile.parent.name
        if version == "0.0.0":
            continue
        version = ".".join(version.split(".")[:2])

        if not pyfile.name.startswith(("pre-", "post-", "end-")):
            continue

        content = pyfile.read_bytes()

        if b"util.dispatch_by_dbuuid" in content:
            # db-specific change, we can ignore this file
            continue

        content_lines = content.splitlines()

        tree = ast.parse(content, filename=pyfile)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "util"
                    and node.func.attr == "rename_module"
                    and not content_lines[node.lineno - 1].endswith(b"# nofml")
                ):
                    if not check_module_rename(version, node.args[1].value, node.args[2].value):
                        rc = 1
                elif (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "util"
                    and node.func.attr == "merge_module"
                    and not content_lines[node.lineno - 1].endswith(b"# nofml")
                ):
                    if not check_module_merge(version, node.args[1].value, node.args[2].value):
                        rc = 1
                else:
                    pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
