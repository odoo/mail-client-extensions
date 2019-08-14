#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
from fnmatch import fnmatch
from glob import glob
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
L = len(HERE) + 1

EXCEPTIONS = {
    os.path.join(HERE, e)
    for e in {
        # scripts that don't need a symlink because they are already handled in other ways
        "report/10.saas~14.1.0/pre-migrate.py",
        "website_account/10.saas~17.1.0/pre-migrate.py",
        "website_subscription/10.saas~17.1.0/pre-01-payment.py",
        "website_subscription/10.saas~17.1.0/pre-migrate.py",
        # explicitly called (util.import_script)
        "sale_payment/saas~11.4.1.0/pre-migrate.py",
        "sale_order_dates/saas~11.4.1.1/pre-migrate.py",
        # views also removed
        "google_base_account/7.saas~2.1.0/pre-10-remove-views.py",
        "account_analytic_analysis/8.saas~6.1.1/pre-rm-views.py",
        "account_invoicing/saas~11.1.1.0/pre-remove.py",
    }
}


def saas(x, y):
    """inject `saas~` in the right place depending of the major version"""
    if x >= 11:
        return "saas~%s.%s" % (x, y)
    return "%s.saas~%s" % (x, y)


def previous_versions(version):
    """
        returns glob-aware wildcard matches for previous versions
        of given versions up to previous major version
    """
    v = list(map(int, version.replace("saas~", "").split(".")))

    if v[1] == 0:
        matches = ["%s.0" % (v[0] - 1,), saas(v[0] - 1, "*")]
    else:
        min_saas = {8: 6, 9: 7, 10: 14}
        matches = ["%s.0" % v[0]] + [
            saas(v[0], "%s.*" % m) for m in range(min_saas.get(v[0], 1), v[1])
        ]

    return matches


def _match_linked_files(version, new, found, reason):
    result = True
    expected = {
        os.path.join(found, f)
        for f in os.listdir(found)
        if os.path.isfile(os.path.join(found, f)) and not fnmatch("*.py[cod]", f)
    }
    for exc in expected & EXCEPTIONS:
        exc = exc[L:]
        print(f"🆗 {exc} manually handled in {new}/{version} ▶︎ [module {reason}]")

    expected -= EXCEPTIONS
    if not expected:
        return True

    target_links = {
        g[L:]: os.path.realpath(g)
        for g in glob(os.path.join(HERE, new, "%s.*" % version, "*"))
        if os.path.islink(g)
    }
    missing = expected - set(target_links.values())
    if not missing:
        for link, target in target_links.items():
            if target in expected:
                ltarget = target[L:]
                print(f"✅ {link} -> {ltarget} ▶︎ [{reason} in {version}]")
    else:
        result = False
        link = os.path.join(HERE, new, "%s.???" % version)[L:]
        for script in missing:
            lscript = script[L:]
            bscript = os.path.basename(script)
            print(f"❌ MISSING SYMLINK: {link}/{bscript} -> {lscript} ▶︎ [{reason} in {version}]")

    return result


def check_module_rename(version, old, new):
    result = True

    for match in previous_versions(version):
        for found in glob(os.path.join(HERE, old, match)):
            old_script_version = os.path.basename(found)
            maybe_link = os.path.join(HERE, new, old_script_version)
            lfound = found[L:]
            link = maybe_link[L:]

            if os.path.islink(maybe_link):
                if os.path.realpath(maybe_link) == found:
                    print(f"✅ {link} -> {lfound} ▶︎ [renamed in {version}]")
                else:
                    result = False
                    print(f"💥 INVALID SYMLINK: {link} -/-> {lfound} ▶︎ [renamed in {version}]")
            elif os.path.exists(maybe_link):
                result = False
                print(
                    f"❗ DUPLICATED SCRIPTS: {link} is a real folder; "
                    "expected symlink to {lfound} ▶︎ [renamed in {version}]"
                )
            elif not _match_linked_files(version, new, found, "renamed"):
                result = False
                print(f"❌ MISSING SYMLINK: {link} -> {lfound} ▶︎ [renamed in {version}]")
    return result


def check_module_merge(version, old, new):
    result = True

    for match in previous_versions(version):
        for found in glob(os.path.join(HERE, old, match)):
            # In case of module merge, we need to track files instead of directories
            # Even if file is symlinked, scripts should be written defensively because
            # table and columns may not exists.
            # XMLIDs should also be named differently based on running version.
            result = _match_linked_files(version, new, found, "merged") and result

    return result


def main():
    rc = 0
    for dirpath, _, filenames in os.walk(os.path.join(HERE, "base")):
        version = os.path.basename(dirpath)
        if version == "0.0.0":
            continue
        version = ".".join(version.split(".")[:2])
        for filename in filenames:
            if not (filename.startswith(("pre-", "post-", "end-")) and filename.endswith(".py")):
                continue
            with open(os.path.join(dirpath, filename)) as fp:
                tree = ast.parse(fp.read(), filename=filename)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "util"
                        and node.func.attr == "rename_module"
                    ):
                        if not check_module_rename(version, node.args[1].s, node.args[2].s):
                            rc = 1
                    elif (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "util"
                        and node.func.attr == "merge_module"
                    ):
                        if not check_module_merge(version, node.args[1].s, node.args[2].s):
                            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
