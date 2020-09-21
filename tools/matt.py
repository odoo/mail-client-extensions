#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter, Action, ArgumentError

from concurrent.futures import ProcessPoolExecutor
from functools import wraps
from pathlib import Path

import tempfile
import os
import subprocess
import sys
from typing import Callable, Generic, NamedTuple, Optional, Union, TypeVar, List, Sequence, Any
from collections import namedtuple

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

    @property
    def ident(self):
        return self.name.split("-")[-1]


REPOSITORIES = [
    Repo("odoo", Path("addons")),
    Repo("enterprise", Path(".")),
    Repo("design-themes", Path(".")),
]
UPGRADE_REPO = Repo("upgrade")


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


def init_repos(options: Namespace) -> bool:
    options.path.mkdir(parents=True, exist_ok=True)

    # TODO parallalize?
    repos = list(REPOSITORIES)
    if options.upgrade_branch != ".":
        repos.append(UPGRADE_REPO)
    for repo in repos:
        p = options.path / repo.name
        if not p.exists():
            if not options.fetch:
                logger.critical("missing %s repository with `--no-fetch` option", repo.name)
                return False

            logger.info("init %s repository", repo.name)
            subprocess.check_call(
                ["git", "clone", "--bare", "-q", repo.remote, repo.name],
                cwd=str(options.path),
            )
            for fetch in ["+refs/heads/*:refs/remotes/origin/*", "+refs/pull/*/head:refs/remotes/origin/pr/*"]:
                subprocess.check_call(
                    ["git", "config", "--local", "--add", "remote.origin.fetch", fetch],
                    cwd=str(p),
                )

        if options.fetch:
            subprocess.check_call(["git", "fetch", "-q"], cwd=str(p))

    conffile = options.path / "odoo.conf"
    if not conffile.exists():
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
        conffile.write_text(
            f"""\
[options]
xmlrpc = False
xmlrpcs = False
netrpc = False
http_enable = False
log_handler = {log_handlers}
"""
        )
    return True


def checkout(repo: Repo, version: str, workdir: Path, options: Namespace) -> bool:
    logger.info("checkout %s at version %s", repo.name, version)
    wd = workdir / repo.name
    wd.mkdir(exist_ok=True)
    gitdir = str(options.path / repo.name)
    # verify branch exists before checkout
    hasref = subprocess.run(["git", "show-ref", "-q", "--verify", f"refs/remotes/origin/{version}"], cwd=gitdir)
    if hasref.returncode != 0:
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
    return True


@result
def process_module(module: str, workdir: Path, options: Namespace) -> None:
    setproctitle(f"matt :: {options.source} -> {options.target} // {module}")
    dbname = f"matt-{module}"

    # create the database
    logger.info("create db %s in version %s", dbname, options.source)
    subprocess.run(["dropdb", "--if-exists", dbname], check=True, stderr=subprocess.DEVNULL)
    subprocess.run(["createdb", dbname], check=True)  # version 7.0 does not create database itself

    re_warn = re.compile(
        rf"^(\d{{4}}-\d\d-\d\d \d\d:\d\d:\d\d,\d{{3}} \d+ (?:WARNING|ERROR|CRITICAL) {dbname} .*)$",
        re.M,
    )

    def odoo(cmd: List[str], version: Version) -> bool:
        cwd = workdir / "odoo" / version.odoo
        ad_path = ",".join(
            str(ad)
            for repo in reversed(REPOSITORIES)  # reverse order to have `enterprise` before `odoo` in 9.0
            for ad in [workdir / repo.name / getattr(version, repo.ident) / repo.addons_dir]
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
            logger.error("Error (returncode=%s) while upgrading module %s:\n%s", p.returncode, module, stdout)
            p.check_returncode()

        warns = "\n".join(re_warn.findall(stdout))
        if warns:
            logger.warning("Some warnings/errors emitted while upgrading module %s:\n%s", module, warns)
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
        logger.info("prepare upgrade tests in db %s", dbname)
        odoo(["--test-tags", "upgrade.test_prepare"], version=options.source)

    # upgrade
    logger.info("upgrade db %s in version %s", dbname, options.target)
    success = odoo(["-u", "all"], version=options.target)

    # tests: validation
    if options.run_tests:
        logger.info("validate upgrade tests in db %s", dbname)
        odoo(["--test-tags", "upgrade.test_check"], version=options.target)

    if success and not options.keep_dbs:
        subprocess.run(["dropdb", "--if-exists", dbname], check=True, stderr=subprocess.DEVNULL)


def matt(options: Namespace) -> int:
    with tempfile.TemporaryDirectory() as workdir_s:
        workdir = Path(workdir_s)
        for repo in REPOSITORIES:
            if not checkout(repo, getattr(options.source, repo.ident), workdir, options):
                return 3
            if not checkout(repo, getattr(options.target, repo.ident), workdir, options):
                return 3
        if options.upgrade_branch != ".":
            if not checkout(UPGRADE_REPO, options.upgrade_branch, workdir, options):
                return 3

        pkgdir = dict()
        for loc in ["source", "target"]:
            version = getattr(options, loc)
            odoodir = workdir / "odoo" / version.odoo
            if (odoodir / "odoo" / "__init__.py").is_file():
                pkgdir[loc] = "odoo"
            elif (odoodir / "openerp" / "__init__.py").is_file():
                pkgdir[loc] = "openerp"
            else:
                logger.critical(
                    "No `odoo` nor `openerp` directory found in odoo branch %s. This tool only works from version 7.0",
                    version.odoo,
                )
                return 2

        # Verify that tests can actually be run by grepping the `--test-tags` options on command line
        if options.run_tests:
            grep = subprocess.run(
                ["git", "grep", "-q", "test-tags", "--", "odoo/tools/config.py"],
                cwd=(workdir / "odoo" / options.source.odoo),
            )
            options.run_tests = grep.returncode == 0
            if not options.run_tests:
                logger.warning("Deactivate tests running as version %r doesn't support them", options.source.odoo)

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

        odoodir = workdir / "odoo" / options.target.odoo
        if (odoodir / pkgdir["target"] / "tools" / "yaml_import.py").exists():
            logger.info("patching yaml_import.py")
            subprocess.run(
                ["git", "apply", "-p0", "--directory", pkgdir["target"], "-"],
                input=YAML_PATCH.encode(),
                check=True,
                cwd=odoodir,
                capture_output=True,
            )

        # create "maintenance" symlinks
        if options.upgrade_branch == ".":
            upgrade_path = Path(__file__).resolve().parent.parent
        else:
            upgrade_path = workdir / "upgrade" / options.upgrade_branch
        # We need to create the symlink in both versions (source and target) to allow upgrade tests discovery
        for loc in ["source", "target"]:
            version = getattr(options, loc)
            maintenance = workdir / "odoo" / version.odoo / pkgdir[loc] / "addons" / "base" / "maintenance"
            if maintenance.is_symlink():  # NOTE: .exists() returns False for broken symlinks
                maintenance.unlink()
            maintenance.symlink_to(upgrade_path)

        # We should also search modules in the $pkgdir/addons of the source
        base_ad = Repo("odoo", Path(pkgdir["source"]) / "addons")

        modules = {
            m.parent.name
            for repo in [base_ad] + REPOSITORIES
            for mod_glob in options.module_globs or ["*"]
            for wd in [workdir / repo.name / getattr(options.source, repo.ident) / repo.addons_dir]
            for m in itertools.chain(
                wd.glob(f"{mod_glob}/__manifest__.py"),
                wd.glob(f"{mod_glob}/__openerp__.py"),
                wd.glob(f"{mod_glob}/__terp__.py"),
            )
            if repo.addons_dir
            if all(not m.parent.relative_to(wd).match(mod_ign) for mod_ign in options.module_ignores or [])
        }
        if not modules:
            logger.error("No module found")
            return 1
        total = len(modules)
        logger.info("Upgrading %d modules", total)

        rc = 0
        with ProcessPoolExecutor(max_workers=min(options.workers, total)) as executor:
            it = executor.map(process_module, modules, itertools.repeat(workdir), itertools.repeat(options))
            for i, r in enumerate(it, 1):
                setproctitle(f"matt :: {options.source} -> {options.target} [{i}/{total}]")
                if isinstance(r, Ok):
                    logger.info("Processed module %d/%d", i, total)
                elif isinstance(r, Err):
                    logger.error("Failed to process module %d/%d: %s", i, total, str(r.err()))
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
                        v = v._replace(**{repo: f"pr/{pr}"})
                    except ValueError:
                        raise ArgumentError(self, f"Invalid repository defined in version: {values!r}")
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
        """,
        formatter_class=RawDescriptionHelpFormatter,
    )
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
    parser.add_argument(
        "--no-fetch", action="store_false", dest="fetch", default=True, help="Do not fetch repositories from remote"
    )

    parser.add_argument("source", action=VersionAction, type=str)
    parser.add_argument("target", action=VersionAction, type=str)

    options = parser.parse_args()
    level = [logging.INFO, logging.WARNING, logging.ERROR][min(options.quiet, 2)]
    logging.basicConfig(level=level, filename=options.log_file)

    setproctitle(f"matt :: {options.source} -> {options.target}")

    if not init_repos(options):
        return 3
    ret = matt(options)

    # cleanup
    repos = list(REPOSITORIES)
    if options.upgrade_branch != ".":
        repos.append(UPGRADE_REPO)
    for repo in repos:
        subprocess.run(["git", "worktree", "prune"], cwd=str(options.path / repo.name))

    return ret


if __name__ == "__main__":
    sys.exit(main())
