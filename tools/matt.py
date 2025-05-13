#!/usr/bin/env python3
# ruff: noqa: ERA001

import hashlib
import itertools
import json
import logging
import os
import re
import shlex
import socket
import subprocess
import sys
import tempfile
import time
from argparse import Action, ArgumentError, ArgumentParser, Namespace, RawDescriptionHelpFormatter
from ast import literal_eval
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack, closing
from functools import wraps
from pathlib import Path
from typing import Any, Callable, FrozenSet, Generic, List, NamedTuple, Optional, Sequence, TypeVar, Union

try:
    from setproctitle import setproctitle  # type: ignore
except ImportError:
    setproctitle = lambda t: None


logger = logging.getLogger("matt")

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Ok(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def ok(self) -> T:
        return self._value


class Err(Generic[E]):
    def __init__(self, e: E) -> None:
        self._e = e

    def err(self) -> E:
        return self._e


Result = Union[Ok[T], Err[E]]


def result(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Result:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)

    return wrapper


class Repo(NamedTuple):
    name: str
    addons_dir: Optional[Path] = None

    @property
    def remote(self):
        return f"git@github.com:odoo/{self.name}.git"

    @property
    def ident(self):
        return self.name.split("-")[-1]

    def branch_required(self, branch):
        if branch.startswith("pr/"):
            return True
        # midly hacky. a non-pr branch is required for non addons-only repositories
        return self.addons_dir != Path(".")

    @classmethod
    def get(cls, name):
        for repo in REPOSITORIES:
            if name in {repo.name, repo.ident}:
                return repo
        raise ValueError(name)


REPOSITORIES = [
    Repo("odoo", Path("addons")),
    Repo("enterprise", Path(".")),
    Repo("design-themes", Path(".")),
]
UPGRADE_REPO = Repo("upgrade")
UPGRADE_UTIL_REPO = Repo("upgrade-util")


# Version = namedtuple("Version", [r.ident for r in REPOSITORIES])
# Mypy doesn't like namedtuple with non-static field list. See:
# https://github.com/python/mypy/issues/848
# https://github.com/python/mypy/issues/4128#issuecomment-598206548
class Version(namedtuple("Version", "odoo enterprise themes")):
    def __str__(self):
        result = []
        main = None
        for repo, value in zip(self._fields, self):
            if value.startswith("pr/"):
                pr = value[3:]
                result.append(f"{repo}#{pr}")
            elif main is None:
                main = value
        if main is not None:
            result.insert(0, main)
        return ":".join(result)

    @property
    def name(self):
        main = str(self).split(":")[0]
        if "#" in main:
            return None
        return main

    @property
    def ints(self):
        if self.name == "master":
            return (99, 99)
        s = list(map(int, self.name.replace("saas-", "").split(".")))
        if len(s) == 1:
            # < 11.0
            major = {range(1, 6): 7, range(6, 7): 8, range(7, 14): 9, range(14, 19): 10}
            for m, n in major.items():
                if s[0] in m:
                    return (n, s[0])
            raise ValueError(self.name)
        return tuple(s)


# Patches
MIGNOINSTALL_PATCH = b"""\
diff --git openerp/modules/migration.py openerp/modules/migration.py
index e0faa77c3a4..4193b2cb6a4 100644
--- openerp/modules/migration.py
+++ openerp/modules/migration.py
@@ -107,7 +107,7 @@ class MigrationManager(object):
                        'post': '[%s>]',
                       }

-        if not (hasattr(pkg, 'update') or pkg.state == 'to upgrade'):
+        if not (hasattr(pkg, 'update') or pkg.state == 'to upgrade') or pkg.state == 'to install':
             return

         def convert_version(version):
"""

YAML_PATCH = b"""\
diff --git tools/yaml_import.py tools/yaml_import.py
index a26d1885ea6..b092f3c836e 100644
--- tools/yaml_import.py
+++ tools/yaml_import.py
@@ -307,7 +307,7 @@ class YamlInterpreter(object):
                     self.id_map[record] = int(id)
                     return None
                 else:
-                    if not self._coerce_bool(record.forcecreate):
+                    if not self._coerce_bool(record.forcecreate, default=True):
                         return None

             #context = self.get_context(record, self.eval_context)
"""

ADDONS_DATA_DIR_PATCH = rb"""\
diff --git openerp/tools/config.py openerp/tools/config.py
index 995d10ec5148..0421abaf8e45 100644
--- openerp/tools/config.py
+++ openerp/tools/config.py
@@ -562,10 +562,10 @@ class configmanager(object):
     def addons_data_dir(self):
         d = os.path.join(self['data_dir'], 'addons', release.series)
         if not os.path.exists(d):
-            os.makedirs(d, 0700)
-        else:
-            assert os.access(d, os.W_OK), \
-                "%s: directory is not writable" % d
+            try:
+                os.makedirs(d, 0700)
+            except OSError:
+                logging.getLogger(__name__).debug('Failed to create addons data dir %s', d)
         return d

     @property
"""

ODOO11_PY38_PATCH = b"""\
diff --git a/odoo/addons/base/ir/ir_qweb/ir_qweb.py b/odoo/addons/base/ir/ir_qweb/ir_qweb.py
index 80535c57dff7..49b234e05413 100644
--- odoo/addons/base/ir/ir_qweb/ir_qweb.py
+++ odoo/addons/base/ir/ir_qweb/ir_qweb.py
@@ -422,10 +422,10 @@ class IrQWeb(models.AbstractModel, QWeb):
     def _get_attr_bool(self, attr, default=False):
         if attr:
             if attr is True:
-                return ast.Name(id='True', ctx=ast.Load())
+                return ast.Constant(True)
             attr = attr.lower()
             if attr in ('false', '0'):
-                return ast.Name(id='False', ctx=ast.Load())
+                return ast.Constant(False)
             elif attr in ('true', '1'):
-                return ast.Name(id='True', ctx=ast.Load())
-        return ast.Name(id=str(attr if attr is False else default), ctx=ast.Load())
+                return ast.Constant(True)
+        return ast.Constant(attr if attr is False else bool(default))
diff --git a/odoo/addons/base/ir/ir_qweb/qweb.py b/odoo/addons/base/ir/ir_qweb/qweb.py
index 59ce3c1936ca..cb7fa90e1b12 100644
--- odoo/addons/base/ir/ir_qweb/qweb.py
+++ odoo/addons/base/ir/ir_qweb/qweb.py
@@ -613,12 +613,12 @@ class QWeb(object):
                         ast.Compare(
                             left=ast.Name(id='content', ctx=ast.Load()),
                             ops=[ast.IsNot()],
-                            comparators=[ast.Name(id='None', ctx=ast.Load())]
+                            comparators=[ast.Constant(None)]
                         ),
                         ast.Compare(
                             left=ast.Name(id='content', ctx=ast.Load()),
                             ops=[ast.IsNot()],
-                            comparators=[ast.Name(id='False', ctx=ast.Load())]
+                            comparators=[ast.Constant(False)]
                         )
                     ]
                 ),
@@ -1247,7 +1247,7 @@ class QWeb(object):
                         keywords=[], starargs=None, kwargs=None
                     ),
                     self._compile_expr0(expression),
-                    ast.Name(id='None', ctx=ast.Load()),
+                    ast.Constant(None),
                 ], ctx=ast.Load())
             )
         ]
@@ -1536,7 +1536,7 @@ class QWeb(object):
                     if isinstance(key, pycompat.string_types):
                         keys.append(ast.Str(s=key))
                     elif key is None:
-                        keys.append(ast.Name(id='None', ctx=ast.Load()))
+                        keys.append(ast.Constant(None))
                     values.append(ast.Str(s=value))

                 # {'nsmap': {None: 'xmlns def'}}
"""


def config_logger(options: Namespace) -> None:
    level = logging.INFO + (10 * options.quiet) - (10 * options.verbose)
    level = max(logging.DEBUG, min(level, logging.CRITICAL))
    logging.basicConfig(level=level, filename=options.log_file, format="%(asctime)s %(levelname)s %(message)s")


def init_repos(options: Namespace) -> bool:
    logger.info("Cache location: %s", options.cache_path)
    options.cache_path.mkdir(parents=True, exist_ok=True)

    # TODO parallalize?
    repos = list(REPOSITORIES)
    if options.upgrade_branch[0] not in "/.":
        repos.append(UPGRADE_REPO)
    if options.upgrade_util_branch[0] not in "/.":
        repos.append(UPGRADE_UTIL_REPO)
    for repo in repos:
        p = options.cache_path / repo.name
        if not p.exists():
            if not options.fetch:
                logger.critical("missing %s repository with `--no-fetch` option", repo.name)
                return False

            logger.info("init %s repository", repo.name)
            subprocess.check_call(
                ["git", "clone", "--bare", "-q", repo.remote, repo.name],
                cwd=str(options.cache_path),
            )
            for fetch in ["+refs/heads/*:refs/remotes/origin/*", "+refs/pull/*/head:refs/remotes/origin/pr/*"]:
                subprocess.check_call(
                    ["git", "config", "--local", "--add", "remote.origin.fetch", fetch],
                    cwd=str(p),
                )

        if options.fetch:
            subprocess.check_call(["git", "fetch", "-q"], cwd=str(p))

    conffile = options.cache_path / "odoo.conf"
    if not conffile.exists() or conffile.stat().st_size == 0:
        log_handlers = ":WARNING,py.warnings:ERROR," + ",".join(
            itertools.chain.from_iterable(
                [f"openerp.{ll}", f"odoo.{ll}"]
                for ll in [
                    "osv.orm.schema:INFO",
                    "models.schema:INFO",
                    "tools.config:ERROR",
                    "tools.misc:INFO",
                    "modules.loading:DEBUG",
                    "modules.graph:CRITICAL",
                    "modules.migration:DEBUG",
                    "addons.base.maintenance.migrations:DEBUG",
                    "upgrade:DEBUG",
                ]
            )
        )
        conffile.write_text(
            f"""\
[options]
xmlrpc = False
xmlrpcs = False
netrpc = False
http_enable = False
log_handler = {log_handlers}
unaccent = True
"""
        )
    return True


def checkout(repo: Repo, version: str, workdir: Path, options: Namespace, stack: ExitStack) -> bool:
    logger.info("checkout %s at version %s", repo.name, version)
    wd = workdir / repo.name
    wd.mkdir(exist_ok=True)
    gitdir = str(options.cache_path / repo.name)
    # verify branch exists before checkout
    hasref = subprocess.run(
        ["git", "show-ref", "-q", "--verify", f"refs/remotes/origin/{version}"], cwd=gitdir, check=False
    )
    if hasref.returncode != 0:
        if not repo.branch_required(version):
            logger.info("unknown ref %r in repository %r: ignoring", version, repo.name)
            return True
        logger.critical("unknown ref %r in repository %r", version, repo.name)
        return False
    subprocess.run(
        [
            "git",
            "--git-dir",
            gitdir,
            "worktree",
            "add",
            "--force",
            wd / version,
            f"origin/{version}",
        ],
        cwd=str(wd),
        check=True,
        # "git worktree" command learned "--quiet" option only in git version 2.19.0
        # In order to handle all git versions, we simply redirect stdout and stderr to /dev/null
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    stack.callback(subprocess.run, ["git", "--git-dir", gitdir, "worktree", "remove", "--force", wd / version])
    return True


def free_port():
    with closing(socket.socket()) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def extract_warnings(dbname, log):
    dt_pid = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3} \d+ ", re.M)
    for warn in re.finditer(f"{dt_pid.pattern}(?:WARNING|ERROR|CRITICAL) {dbname} .*$", log, re.M):
        next_line = dt_pid.search(log, warn.end())
        end = next_line.start() - 1 if next_line is not None else warn.end()
        yield log[slice(warn.start(), end)]


def parse_release(workdir: Path, version: Version):
    for subdir in ["odoo", "openerp"]:
        release = workdir / "odoo" / version.odoo / subdir / "release.py"
        if release.is_file():
            break
    else:
        raise ValueError("Cannot find `release.py` file")

    # strict minimal builtins. `__import__` is not defined, so no import is possible.
    builtins = {
        "str": str,
        "map": map,
    }
    global_dict = {"__builtins__": builtins}
    local_dict = {}

    code = compile(release.read_text(), "", mode="exec")
    eval(code, global_dict, local_dict)
    return local_dict.get("series", local_dict.get("serie", version.name.replace("-", "~")))


@result
def process_module(modules: FrozenSet[str], workdir: Path, options: Namespace) -> None:
    config_logger(options)
    module_plus = "+".join(sorted(modules))
    setproctitle(f"matt :: {options.source} -> {options.target} // {module_plus}")
    dbname = f"matt-{module_plus}"
    if len(dbname) >= 64:
        modhash = hashlib.sha3_224(module_plus.encode()).hexdigest()
        dbname = f"matt-__{modhash}"

    l10n_modules = {m[m.index("l10n_") :].split("_")[1].lower(): m for m in modules if "l10n_" in m}
    if len(l10n_modules) > 1:
        raise ValueError("installing multiple `l10n_` modules is not yet supported")

    # create the database
    logger.info("create db %s in version %s", dbname, options.source)
    subprocess.run(["dropdb", "--if-exists", dbname], check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["createdb", dbname], check=True)  # version 7.0 does not create database itself

    extensions = ["unaccent"]
    query = "SELECT usesuper FROM pg_user WHERE usename = CURRENT_USER"
    issuper = subprocess.check_output(["psql", "--no-psqlrc", "--quiet", "--tuples-only", "-d", dbname, "-c", query])
    if issuper.decode().strip() == "t":
        extensions.append("pg_trgm")

    for ext in extensions:
        query = f"CREATE EXTENSION IF NOT EXISTS {ext}"
        subprocess.run(["psql", "--no-psqlrc", "--quiet", "-d", dbname, "-c", query], check=False)  # may fail

    # now mark `unaccent` as IMMUTABLE, if possible. Needed for some indexes
    query = r"""
    DO $$
        BEGIN
            ALTER FUNCTION unaccent(text) IMMUTABLE;
        EXCEPTION
           WHEN insufficient_privilege THEN
        END;
    $$;
    """
    subprocess.run(["psql", "--no-psqlrc", "--quiet", "-d", dbname, "-c", query], check=True)

    env = dict(
        os.environ,
        MATT="1",
        ODOO_UPG_DB_SOURCE_VERSION=parse_release(workdir, options.source),
        ODOO_UPG_DB_TARGET_VERSION=parse_release(workdir, options.target),
    )

    def odoo(cmd: List[str], *, version: Version, python: Optional[Path], module: str = module_plus) -> bool:
        cwd = workdir / "odoo" / version.odoo
        ad_path = ",".join(
            str(ad)
            for repo in reversed(REPOSITORIES)  # reverse order to have `enterprise` before `odoo` in 9.0
            for ad in [workdir / repo.name / getattr(version, repo.ident) / repo.addons_dir]
            if ad.exists()
        )

        odoo_bin = "./odoo-bin" if (cwd / "odoo-bin").is_file() else "./openerp-server"
        py_bin = [str(python)] if python else []
        cmd = [
            *py_bin,
            odoo_bin,
            "-c",
            str(options.cache_path / "odoo.conf"),
            "--addons-path",
            ad_path,
            "-d",
            dbname,
            "--without-demo",
            "" if options.demo else "1",  # option not read from config file; should be on command line
            "--stop-after-init",
            *cmd,
        ]
        if options.run_tests:
            cmd += ["--http-port", str(free_port())]

        if version in options.upgrade_path:
            cmd += ["--upgrade-path", options.upgrade_path[version]]

        step = "upgrading" if "-u" in cmd else "testing" if "--test-tags" in cmd else "installing"
        logger.debug("%s module set %s at version %s", step, module, version)
        logger.debug("[+] %s", " ".join(shlex.quote(arg) for arg in cmd))
        p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)
        stdout = p.stdout.decode()
        if p.returncode:
            logger.error("Error (returncode=%s) while %s module set %s:\n%s", p.returncode, step, module, stdout)
            p.check_returncode()

        warns = "\n".join(extract_warnings(dbname, stdout))
        if warns:
            output = stdout if logger.isEnabledFor(logging.DEBUG) else warns
            logger.warning("Some warnings/errors emitted while %s module set %s:\n%s", step, module, output)
            return False
        return True

    source = {"version": options.source, "python": options.source_python_bin}
    target = {"version": options.target, "python": options.target_python_bin}

    # For versions >= 9.0, the main partner needs to be in the country of the installed l10n module.
    # If we cannot determine the version name, we assume than we try to upgrade from a version >= 9.0.
    if l10n_modules and (not options.source.name or ((9, 0) <= options.source.ints < (16, 0))):
        cc, module = l10n_modules.popitem()
        # create a `base` db and modify the non-demo partners country before installing the localization
        odoo(["-i", "base"], **source, module="base")

        # 3 cases:
        # - `module` should not be changed. Just the country code is different (uk, generic, syscohada)
        # - `module` is a common dependency of multiple `l10n_{cc}` modules and is not useful on itself (latam, multilang)
        # - `module` is independent of any `l10n_{cc}` module, but required one to be installed (eu)
        cc_map = {
            #     (country code, actual module to test, explicit l10n module to pre-install)
            "eu": ("be", module, "l10n_be"),
            "uk": ("gb", module, None),
            "latam": ("cl", "l10n_cl", None),
            "syscohada": ("cd", module, None),
            "generic": ("us", module, None),
            "multilang": ("be", "l10n_be", None),
        }
        cc, new_module, l10n_module = cc_map.get(cc, (cc, module, None))
        if new_module != module:
            modules = (modules - {module}) | {new_module}

        sql = f"""
            UPDATE res_partner p
               SET country_id = c.country_id,
                   state_id = c.state_id
              FROM (
                    SELECT c.id as country_id,
                           s.id as state_id
                      FROM res_country c
                 LEFT JOIN res_country_state s ON s.country_id = c.id
                     WHERE lower(c.code) = '{cc}'
                     LIMIT 1
              ) c,
              ir_model_data x
             WHERE x.model = 'res.partner' AND x.res_id = p.id
               AND x.name IN ('main_partner', 'partner_root', 'partner_admin', 'public_partner')
        """
        sql = re.sub(r"\s{2,}", " ", sql).strip()  # one-line the query

        logger.debug("locate partners in %s", cc.upper())
        subprocess.run(["psql", "--no-psqlrc", "--quiet", "-d", dbname, "-c", sql], check=True)

        if l10n_module:
            # Explicitly install the localisation.
            odoo(["-i", l10n_module], **source, module=l10n_module)

    odoo(["-i", ",".join(modules)], **source)

    # tests: preparation
    if options.run_tests:
        logger.info("prepare upgrade tests in db %s", dbname)
        odoo(["--test-tags", "upgrade.test_prepare"], **source)

    # upgrade
    logger.info("upgrade db %s in version %s", dbname, options.target)
    success = odoo(["-u", "all"], **target)

    # tests: validation
    if options.run_tests:
        logger.info("validate upgrade tests in db %s", dbname)
        odoo(["--test-tags", "upgrade.test_check,upgrade_unit"], **target)

    if success and not options.keep_dbs:
        subprocess.run(["dropdb", "--if-exists", dbname], check=True, stderr=subprocess.DEVNULL)


def dump_progress(options: Namespace, start: int, done: int, total: int) -> None:
    outfile = options.progress_file
    if not outfile:
        return
    progress = {
        "start": start,
        "done": done,
        "total": total,
        "at": int(time.time()),
    }
    outfile.write_text(json.dumps(progress))


def matt(options: Namespace) -> int:
    with tempfile.TemporaryDirectory() as workdir_s, ExitStack() as stack:
        workdir = Path(workdir_s)
        for repo in REPOSITORIES:
            if not checkout(repo, getattr(options.source, repo.ident), workdir, options, stack):
                return 3
            if not checkout(repo, getattr(options.target, repo.ident), workdir, options, stack):
                return 3
        if options.upgrade_branch[0] not in "/.":  # noqa: SIM102
            if not checkout(UPGRADE_REPO, options.upgrade_branch, workdir, options, stack):
                return 3
        if options.upgrade_util_branch[0] not in "/.":  # noqa: SIM102
            if not checkout(UPGRADE_UTIL_REPO, options.upgrade_util_branch, workdir, options, stack):
                return 3

        pkgdir = {}
        for loc in ["source", "target"]:
            version = getattr(options, loc)
            odoodir = workdir / "odoo" / version.odoo
            if any((odoodir / "odoo" / init).is_file() for init in ("init.py", "__init__.py")):
                pkgdir[loc] = "odoo"
            elif (odoodir / "openerp" / "__init__.py").is_file():
                pkgdir[loc] = "openerp"
                # For very old versions (< 8.0), the migration engine should be patched to no run upgrade scripts at module
                # installation.
                patched = subprocess.run(
                    ["git", "apply", "-p0", "-"],
                    input=MIGNOINSTALL_PATCH,
                    check=False,
                    cwd=odoodir,
                    capture_output=True,
                )
                if patched.returncode == 0:
                    logger.info("migration engine patched in %s version", loc)

                # Patch the datadir addons path to avoid a race condition
                # (adapted from odoo/odoo@4715d18e122554972ca9d20ce3d361dcbc0e646c)
                patched = subprocess.run(
                    ["git", "apply", "-p0", "-"],
                    input=ADDONS_DATA_DIR_PATCH,
                    check=False,
                    cwd=odoodir,
                    capture_output=True,
                )
                if patched.returncode == 0:
                    logger.info("datadir addons path handling patched in %s version", loc)

            else:
                logger.critical(
                    "No `odoo` nor `openerp` directory found in odoo branch %s. This tool only works from version 7.0",
                    version.odoo,
                )
                return 2

            if sys.version_info >= (3, 8) and (version.name == "11.0" or version.name.startswith("saas~11.")):
                # Patch version 11 to be compatible with python 3.8
                # Backport of odoo/odoo@d73b44a46ffbf3de0ec3ad6b6ec6d3f161bd9474
                patched = subprocess.run(
                    ["git", "apply", "-p0", "-"],
                    input=ODOO11_PY38_PATCH,
                    check=False,
                    cwd=odoodir,
                    capture_output=True,
                )
                if patched.returncode == 0:
                    logger.info(
                        "qweb compilation code patched in %s version (%s) to be compatible with python >= 3.8",
                        loc,
                        version.name,
                    )

        # Patch YAML import to allow creation of new records during update.
        # This is a long standing bug present since the start (yeah, even in 6.0).
        # It's only problematic when upgrading with demo data.
        odoodir = workdir / "odoo" / options.target.odoo
        if (odoodir / pkgdir["target"] / "tools" / "yaml_import.py").exists():
            logger.info("patching yaml_import.py")
            subprocess.run(
                ["git", "apply", "-p0", "--directory", pkgdir["target"], "-"],
                input=YAML_PATCH,
                check=True,
                cwd=odoodir,
                capture_output=True,
            )

        # Verify that tests can actually be run by grepping the `--test-tags` options on command line
        if options.run_tests:
            grep = subprocess.run(
                ["git", "grep", "-q", "test-tags", "--", "odoo/tools/config.py"],
                cwd=(workdir / "odoo" / options.source.odoo),
                check=False,
            )
            options.run_tests = grep.returncode == 0
            if not options.run_tests:
                logger.warning("Deactivate tests running as version %r doesn't support them", options.source.odoo)

        # create "maintenance" symlinks
        if options.upgrade_branch[0] in "/.":
            upgrade_path = (
                Path(__file__).resolve().parent.parent
                if options.upgrade_branch == "."
                else Path(options.upgrade_branch).resolve()
            )
        else:
            upgrade_path = workdir / UPGRADE_REPO.name / options.upgrade_branch

        if options.upgrade_util_branch[0] in "/.":
            upgrade_util_path = (
                Path.cwd() if options.upgrade_util_branch == "." else Path(options.upgrade_util_branch).resolve()
            )
        else:
            upgrade_util_path = workdir / UPGRADE_UTIL_REPO.name / options.upgrade_util_branch

        src_dir = upgrade_util_path / "src"
        mig_dir = upgrade_path / "migrations"
        embedded_util = (mig_dir / "util" / "__init__.py").exists() or (mig_dir / "util.py").exists()

        # __import__('pudb').set_trace()
        # We need to create the symlink in both versions (source and target) to allow upgrade tests discovery
        options.upgrade_path = {}
        for loc in ["source", "target"]:
            version = getattr(options, loc)

            support_upgrade_path = subprocess.run(
                ["git", "grep", "-q", "upgrade-path", "--", "odoo/tools/config.py"],
                cwd=(workdir / "odoo" / version.odoo),
                check=False,
            )
            if support_upgrade_path.returncode == 0 and not embedded_util:
                options.upgrade_path[version] = f"{src_dir},{mig_dir}"
            else:
                # For old versions, we should do symlinks
                if loc == "source" and not embedded_util:
                    for f in src_dir.rglob("*"):
                        if not f.is_file():
                            continue
                        r = f.relative_to(src_dir)
                        td = mig_dir / r.parent
                        td.mkdir(parents=True, exist_ok=True)
                        sl = td / r.name
                        if sl.is_symlink():
                            sl.unlink()
                        if not sl.exists():
                            sl.symlink_to(f)
                            if options.upgrade_branch[0] in "/.":
                                # do not polute the local directory.
                                stack.callback(sl.unlink)
                        elif sl.match("*/tests/__init__.py") and version.ints[0] == 12:
                            # merge content
                            content = sl.read_text()
                            sl.write_text(f"{content}\n{f.read_text()}")
                            stack.callback(sl.write_text, content)

                    # Now that we have done the symlinks, we cannot use `--upgrade-path` for the target version,
                    # else it we will ends with duplicated upgrade scripts. Consider util has being embedded.
                    # This is only problematic for saas-12.3 -> 13.0 upgrades.
                    embedded_util = True

                maintenance = workdir / "odoo" / version.odoo / pkgdir[loc] / "addons" / "base" / "maintenance"
                if maintenance.is_symlink():  # NOTE: .exists() returns False for broken symlinks
                    maintenance.unlink()
                maintenance.symlink_to(upgrade_path)

        # We should also search modules in the $pkgdir/addons of the source
        base_ad = Repo("odoo", Path(pkgdir["source"]) / "addons")

        def get_deps(manifest: Path) -> List[str]:
            return list(literal_eval(manifest.read_text()).get("depends", []))

        def glob(mod_glob: str) -> FrozenSet[str]:
            filter_leaf_modules = mod_glob == "*"

            if mod_glob == "**":
                mod_glob = "*"  # normal glob that will match all modules

            modules = {
                m.parent.name: get_deps(m) if filter_leaf_modules else []
                for repo in [base_ad, *REPOSITORIES]
                for wd in [workdir / repo.name / getattr(options.source, repo.ident) / repo.addons_dir]
                for m in itertools.chain(
                    wd.glob(f"{mod_glob}/__manifest__.py"),
                    wd.glob(f"{mod_glob}/__openerp__.py"),
                    wd.glob(f"{mod_glob}/__terp__.py"),
                )
                if repo.addons_dir
                if all(not m.parent.relative_to(wd).match(mod_ign) for mod_ign in options.module_ignores or [])
                # Don't match test modules via wilcards, unless explicitly asked for.
                if "test" not in m.parent.name or "test" in mod_glob
            }

            all_deps = frozenset(itertools.chain.from_iterable(modules.values()))
            return frozenset(modules.keys()) - all_deps

        modules = {
            p
            for mod_glob in options.module_globs or ["*"]
            for p in map(frozenset, itertools.product(*(glob(s.strip()) for s in mod_glob.split("+"))))
            if len(p) == mod_glob.count("+") + 1
        }

        if not modules:
            logger.error("No module found")
            return 1
        total = len(modules)
        logger.info("Upgrading %d module sets", total)

        rc = 0
        with ProcessPoolExecutor(max_workers=min(options.workers, total)) as executor:
            st = int(time.time())
            dump_progress(options, st, 0, total)
            it = executor.map(process_module, modules, itertools.repeat(workdir), itertools.repeat(options))
            for i, r in enumerate(it, 1):
                dump_progress(options, st, i, total)
                setproctitle(f"matt :: {options.source} -> {options.target} [{i}/{total}]")
                if isinstance(r, Ok):
                    logger.info("Processed module set %d/%d", i, total)
                elif isinstance(r, Err):
                    logger.error("Failed to process module set %d/%d: %s", i, total, str(r.err()))
                    rc = 1

    logger.info("Job done!")
    return rc


class VersionAction(Action):
    def __call__(
        self, parser: ArgumentParser, namespace: Namespace, values: Union[str, Sequence[Any], None], option_string=None
    ) -> None:
        v = Version(*[None] * len(Version._fields))
        assert isinstance(values, str)
        fallback = None
        for part in values.split(":"):
            for sep in "#/":
                repo, _, pr = part.partition(sep)
                if pr:
                    try:
                        v = v._replace(**{Repo.get(repo).ident: f"pr/{pr}"})
                    except ValueError:
                        raise ArgumentError(self, f"Invalid repository defined in version: {values!r}") from None
                    break
            else:
                if fallback is not None:
                    raise ArgumentError(self, f"Invalid version definition: {values!r}")
                fallback = part

        field: str
        for field in Version._fields:
            if getattr(v, field) is None:
                if fallback is None:
                    raise ArgumentError(self, f"Incomplete version definition: {values!r}")
                v = v._replace(**{field: fallback})

        setattr(namespace, self.dest, v)


def glob_plus(pattern):
    if "***" in pattern:
        raise ValueError(pattern)

    for s in map(str.strip, pattern.split("+")):
        if not s:
            break
        if s != "**" and "**" in s:
            # ** is only valid on itself, not as part of a glob
            break
    else:  # no break
        return pattern

    raise ValueError(pattern)


def main() -> int:
    parser = ArgumentParser(
        description="matt :: Migrate All The Things",
        epilog="""\
The `source` and `target` arguments have the following format:
    BRANCH
    BRANCH:odoo#3303
    BRANCH:odoo#3303:enterprise#40
    BRANCH:odoo/3303                ; a `/` is also allowed as separator

It allows to test upgrades against development branches.

The patterns `*` and `**` refer to `all leaf modules` and `all modules`.
To test module combinations, use the `+` character. i.e.
   ./matt.py -m note+calendar 16.0 17.0

`*` and `**` also works in combinations. `l10n_be+delivery_*` expand to `l10n_be+delivery_bpost`, `l10n_be+delivery_dhl`,
`l10n_be+delivery_easypost`, etc.
`*+*` expand to a combination of all leaf modules.
`**+**` expand to a combination of all modules.
Identity combinations will be ignored. `crm+crm` won't yield anything.
Duplicated combinations are ignored. `payment_*+payment_*` yield all combinations of payment modules only once.
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--cache",
        "-p",  # kept for retro-compatibility
        "--path",
        dest="cache_path",
        type=Path,
        default=Path(f"{os.getenv('XDG_CACHE_HOME', '~/.cache')}/matt").expanduser(),
        help="Cache Directory (default: %(default)s)",
    )
    parser.add_argument(
        "-b",
        "--upgrade-branch",
        type=str,
        default="master",
        help="`upgrade` branch to use. Pull-Requests are via the `pr/` prefix (i.e. `pr/971`). "
        "You can also use a path (starting with `/` or `.`) to test local patches."
        "(default: %(default)s)",
    )
    parser.add_argument(
        "-u",
        "--upgrade-util-branch",
        type=str,
        default="master",
        help="`upgrade-util` branch to use. Pull-requests are via the `pr/` prefix (i.e. `pr/971`). "
        "You can also use a path (starting with `/` or `.`) to test local patches."
        "(default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--modules",
        type=glob_plus,
        action="append",
        dest="module_globs",
        help="Modules (glob+) to upgrade (default: *)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        type=str,
        action="append",
        dest="module_ignores",
        help="Modules (glob) to ignore. Done *after* matching with `--modules` flag",
    )
    cpus = os.cpu_count() or 1
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=max(1, cpus // 2),
        choices=range(1, cpus + 1),
        metavar=f"{{1..{cpus}}}",
        help="Number of workers (default: %(default)s)",
    )

    parser.add_argument("-l", "--log-file", type=Path)
    parser.add_argument("--progress-file", type=Path)
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        dest="quiet",
        default=0,
        help="quiet level. `-q` to log warnings, `-qq` to only log failed upgrades",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        default=0,
    )
    parser.add_argument(
        "-k",
        "--keep-databases",
        action="store_true",
        dest="keep_dbs",
        default=False,
        help="Do not drop databases after successful upgrade",
    )
    parser.add_argument(
        "--no-demo", action="store_false", dest="demo", default=True, help="Create databases without demo data"
    )
    parser.add_argument("-t", "--tests", action="store_true", dest="run_tests", default=False, help="Run upgrade tests")
    parser.add_argument("--no-tests", action="store_false", dest="run_tests", help="Run upgrade tests")
    parser.add_argument(
        "--no-fetch", action="store_false", dest="fetch", default=True, help="Do not fetch repositories from remote"
    )

    parser.add_argument("--source-python-bin", type=Path, default=None)
    parser.add_argument("--target-python-bin", type=Path, default=None)

    parser.add_argument("source", action=VersionAction, type=str)
    parser.add_argument("target", action=VersionAction, type=str)

    options = parser.parse_args()

    config_logger(options)
    setproctitle(f"matt :: {options.source} -> {options.target}")

    if not init_repos(options):
        return 3

    return matt(options)


if __name__ == "__main__":
    sys.exit(main())
