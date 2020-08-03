#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace

from concurrent.futures import ProcessPoolExecutor
from functools import wraps
from pathlib import Path

import tempfile
import os
import subprocess
import sys
from typing import Callable, Generic, NamedTuple, Optional, Union, TypeVar, List

import re
import logging
import itertools

try:
    from setproctitle import setproctitle  # type: ignore
except ImportError:
    setproctitle = lambda t: None


logger = logging.getLogger(__name__)

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


REPOSITORIES = [
    Repo("odoo", Path("addons")),
    Repo("enterprise", Path(".")),
    Repo("design-themes", Path(".")),
]
UPGRADE_REPO = Repo("upgrade")


def init_repos(options: Namespace) -> None:
    options.path.mkdir(parents=True, exist_ok=True)

    # TODO parallalize?
    for repo in REPOSITORIES + [UPGRADE_REPO]:
        p = options.path / repo.name
        p.mkdir(exist_ok=True)
        if not (p / "master").exists():
            logger.info("init %s repo", repo.name)
            subprocess.run(
                ["git", "clone", "-q", repo.remote, "--branch", "master", "master"], cwd=str(p), check=True,
            )
            # also fetch PR under pr/ namespace
            subprocess.run(
                [
                    "git",
                    "config",
                    "--local",
                    "--add",
                    "remote.origin.fetch",
                    "+refs/pull/*/head:refs/remotes/origin/pr/*",
                ],
                cwd=str(p / "master"),
                check=True,
            )

    # create a cross-version config file
    log_handlers = ":WARNING,py.warnings:ERROR," + ",".join(
        itertools.chain.from_iterable(
            [f"openerp.{ll}", f"odoo.{ll}"]
            for ll in """
        osv.orm.schema:INFO models.schema:INFO
        tools.misc:INFO
        modules.loading:DEBUG modules.graph:CRITICAL
        modules.migration:DEBUG
        addons.base.maintenance.migrations:DEBUG upgrade:DEBUG
    """.split()
        )
    )
    (options.path / "odoo.conf").write_text(
        f"""\
[options]
xmlrpc = False
xmlrpcs = False
netrpc = False
http_enable = False
log_handler = {log_handlers}
"""
    )


def checkout(repo: Repo, version: str, options: Namespace) -> None:
    logger.info("checkout %s at version %s", repo.name, version)
    wd = options.path / repo.name
    subprocess.run(["git", "fetch", "-q"], cwd=wd / "master", check=True)
    if (wd / version).exists():
        subprocess.run(["git", "reset", "-q", "--hard", "@{upstream}"], cwd=wd / version, check=True)
    else:
        # verify branch exists before checkout
        hasref = subprocess.run(
            ["git", "show-ref", "-q", "--verify", f"refs/remotes/origin/{version}"], cwd=wd / "master"
        )
        if hasref.returncode != 0:
            return
        subprocess.run(
            [
                "git",
                "--git-dir",
                "master/.git",
                "worktree",
                "add",
                "--guess-remote",
                "--track",
                "-B",
                version,
                version,
                f"origin/{version}",
            ],
            cwd=wd,
            check=True,
            # "git worktree" command learned "--quiet" option only in git version 2.19.0
            # In order to handle all git versions, we simply redirect stdout to /dev/null
            stdout=subprocess.DEVNULL,
        )


@result
def process_module(module: str, options: Namespace) -> None:
    setproctitle(f"matt :: {options.source} -> {options.target} // {module}")
    dbname = f"matt-{module}"

    # create the database
    logger.info("create db %s in version %s", dbname, options.source)
    subprocess.run(["dropdb", "--if-exists", dbname], check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["createdb", dbname], check=True)  # version 7.0 does not create database itself

    re_warn = re.compile(
        rf"^(\d{{4}}-\d\d-\d\d \d\d:\d\d:\d\d,\d{{3}} \d+ (?:WARNING|ERROR|CRITICAL) {dbname} .*)$", re.M,
    )

    def odoo(cmd: List[str], version: str) -> bool:
        cwd = options.path / "odoo" / version
        ad_path = ",".join(
            str(ad)
            for repo in reversed(REPOSITORIES)  # reverse order to have `enterprise` before `odoo` in 9.0
            # if (ad := options.path / repo.name / version / repo.addons_dir).exists()
            for ad in [options.path / repo.name / version / repo.addons_dir]
            if ad.exists()
        )

        odoo_bin = "./odoo-bin" if (cwd / "odoo-bin").is_file() else "./openerp-server"
        cmd = [
            odoo_bin,
            "-c",
            str(options.path / "odoo.conf"),
            "--addons-path",
            ad_path,
            "-d",
            dbname,
            "--without-demo",
            "" if options.demo else "1",  # option not read from config file; should be on command line
            "--stop-after-init",
        ] + cmd
        p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = p.stdout.decode()
        if p.returncode:
            logger.error(
                "Error (returncode=%s) while upgrading module %s:\n%s", p.returncode, module, stdout,
            )
            p.check_returncode()

        warns = "\n".join(re_warn.findall(stdout))
        if warns:
            logger.warning(
                "Some warnings/errors emitted while upgrading module %s:\n%s", module, warns,
            )
            return False
        return True

    if module.startswith("l10n_"):
        # create a `base` db and modify the partners country before installing the localization
        odoo(["-i", "base"], version=options.source)
        cc = module.split("_")[1].lower()
        sql = f"UPDATE res_partner SET country_id = (SELECT id FROM res_country WHERE lower(code)='{cc}')"
        subprocess.run(["psql", "--no-psqlrc", "--quiet", "-d", dbname, "-c", sql], check=True)

    odoo(["-i", module], version=options.source)

    # tests: preparation
    if options.run_tests:
        odoo(["--test-tags", "upgrade.test_prepare"], version=options.source)

    # upgrade
    logger.info("upgrade db %s in version %s", dbname, options.target)
    success = odoo(["-u", "all"], version=options.target)

    # tests: validation
    if options.run_tests:
        odoo(["--test-tags", "upgrade.test_check"], version=options.target)

    if success and not options.keep_dbs:
        subprocess.run(["dropdb", "--if-exists", dbname], check=True, stderr=subprocess.DEVNULL)


def matt(options: Namespace) -> int:
    for repo in REPOSITORIES:
        checkout(repo, options.source, options)
        checkout(repo, options.target, options)
    if options.upgrade_branch != ".":
        checkout(UPGRADE_REPO, options.upgrade_branch, options)

    odoodir = options.path / "odoo" / options.target
    if (odoodir / "odoo" / "__init__.py").is_file():
        pkgdir = "odoo"
    elif (odoodir / "openerp" / "__init__.py").is_file():
        pkgdir = "openerp"
    else:
        logger.critical(
            "No `odoo` nor `openerp` directory found in odoo branch %s. This tool only works from version 7.0",
            options.target,
        )
        return 2

    # Verify that tests can actually be run by grepping the `--test-tags` options on command line
    if options.run_tests:
        grep = subprocess.run(
            ["git", "grep", "-q", "test-tags", "--", "odoo/tools/config.py"],
            cwd=(options.path / "odoo" / options.source),
        )
        options.run_tests = grep.returncode == 0

    # Patch YAML import to allow creation of new records during update.
    # This is a long standing bug present since the start (yeah, even in 6.0).
    # It's only problematic when upgrading with demo data.
    YAML_PATCH = """\
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

    if (odoodir / pkgdir / "tools" / "yaml_import.py").exists():
        logger.info("patching yaml_import.py")
        subprocess.run(
            ["git", "apply", "-p0", "--directory", pkgdir, "-"],
            input=YAML_PATCH.encode(),
            check=True,
            cwd=odoodir,
            capture_output=True,
        )

    # create symlink
    maintenance = odoodir / pkgdir / "addons" / "base" / "maintenance"
    if maintenance.exists():
        maintenance.unlink()
    if options.upgrade_branch == ".":
        upgrade_path = Path(__file__).resolve().parent.parent
    else:
        upgrade_path = options.path / "upgrade" / options.upgrade_branch
    maintenance.symlink_to(upgrade_path)

    modules = [
        m.parent.name
        for repo in REPOSITORIES
        for mod_glob in options.module_globs or ["*"]
        for wd in [options.path / repo.name / options.source / repo.addons_dir]
        for m in itertools.chain(
            wd.glob(f"{mod_glob}/__manifest__.py"),
            wd.glob(f"{mod_glob}/__openerp__.py"),
            wd.glob(f"{mod_glob}/__terp__.py"),
        )
        if repo.addons_dir
        if all(not m.parent.relative_to(wd).match(mod_ign) for mod_ign in options.module_ignores or [])
    ]
    if not modules:
        logger.error("No module found")
        return 1
    total = len(modules)
    logger.info("Upgrading %d modules", total)

    rc = 0
    with ProcessPoolExecutor(max_workers=min(options.workers, total)) as executor:
        it = executor.map(process_module, modules, itertools.repeat(options))
        for i, r in enumerate(it, 1):
            if isinstance(r, Ok):
                logger.info("Processed module %d/%d", i, total)
            elif isinstance(r, Err):
                logger.error("Failed to process module %d/%d: %s", i, total, str(r.err()))
                rc = 1

    logger.info("Job done!")
    return rc


def main() -> int:

    parser = ArgumentParser(description="matt :: Migrate All The Things")
    parser.add_argument(
        "-p",
        "--path",
        type=Path,
        default=Path(f"{tempfile.gettempdir()}/matt"),
        help="Working directory (default: %(default)s)",
    )
    parser.add_argument(
        "-b",
        "--upgrade-branch",
        type=str,
        default="master",
        help="Upgrade branch to use. Pull-Requests are via the `pr/` prefix (i.e. `pr/971`). "
        "To use the current working directory (with the local patches), use `.` as upgrade branch. "
        "(default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--modules",
        type=str,
        action="append",
        dest="module_globs",
        help="Modules (glob) to upgrade (default: *)",
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
    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        dest="quiet",
        default=0,
        help="quiet level. `-q` to log warnings, `-qq` to only log failed upgrades",
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

    parser.add_argument("source")
    parser.add_argument("target")

    options = parser.parse_args()
    level = [logging.INFO, logging.WARNING, logging.ERROR][min(options.quiet, 2)]
    logging.basicConfig(level=level, filename=options.log_file)

    setproctitle(f"matt :: {options.source} -> {options.target}")

    init_repos(options)
    return matt(options)


if __name__ == "__main__":
    sys.exit(main())
