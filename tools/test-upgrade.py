#!/usr/bin/env python3
import argparse
import logging
import os.path
import signal
import subprocess
import sys
from logging.handlers import WatchedFileHandler

import psycopg2

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
_logger = logging.getLogger(__name__)


class Odoo:
    def __init__(self, database, logfile=None, log_level=None, dry_run=False, upgrade_path=None):
        self.logfile = logfile
        self.database = database
        self.dry_run = dry_run
        self.log_level = log_level
        self.upgrade_path = upgrade_path

    def db_exists(self):
        try:
            conn = psycopg2.connect("dbname='%s'" % self.database)
            conn.close()
        except psycopg2.OperationalError:
            return False
        return True

    def drop_db(self):
        _logger.info("Dropping db %s ", self.database)
        self._exec(["dropdb", self.database], ("An error occured while droping db %s", self.database))

    def restore_db(self, template):
        _logger.info("Restoring db %s to %s", template, self.database)
        self._exec(
            ["createdb", self.database, "-T", template],
            ("An error occured while restoring db %s to %s", template, self.database),
        )

    def dump_db(self, name):
        _logger.info("Saving db to %s", name)
        self._exec(["createdb", name, "-T", self.database], ("An error occured while saving db to %s", name))

    def run(self, exec_path, addons_path, *args):
        cmd = [exec_path, "--addons-path", ",".join(addons_path), "-d", self.database, "--stop-after-init"] + list(args)
        if self.logfile:
            cmd += ["--logfile", self.logfile]
        if self.log_level:
            cmd += ["--log-level", self.log_level]
        if self.upgrade_path:
            cmd += ["--upgrade-path", self.upgrade_path]
        if not self.dry_run:
            _logger.info(" ".join(cmd))
        self._exec(cmd, ["An error occured, exiting"])

    def _checkout(self, path, version):
        msg = ("something went wrong checkouting %s on %s", version, path)

        def preexec_function():
            signal.signal(signal.SIGINT, signal.SIG_IGN)  # avoid to interrupt checkout

        self._exec(["git", "-C", path, "checkout", version], msg, preexec_function=preexec_function)

    def _exec(self, cmd, error_message, quit_on_failure=True, preexec_function=None):
        if self.dry_run:
            _logger.info(" ".join(cmd))
            return
        proc = subprocess.Popen(cmd, preexec_fn=preexec_function)
        res = proc.wait()
        if res != 0:
            _logger.error(*error_message)
            if quit_on_failure:
                sys.exit(1)

    def checkout(self, versions, addons_path):
        """
        checkout given versions in all addons_path.
        If version contains multiple elements, will checkout each version in each addons path
        If version contains one element, will checkout this version in all addons path
        """
        if len(versions) != len(addons_path):
            if len(versions) != 1:
                raise Exception("Multiple version given (%s) not matching addons_path length (%s)" % versions)
            else:
                versions = versions * len(addons_path)
        for version, path in zip(versions, addons_path):
            self._checkout(path, version)


def normalize_path(path, relative_to_file=False):
    base_directory = os.getenv("PWD")  # CAUTION ! dont use os.getcwd()
    # getcwd and abspath will return realpath
    # example:
    # root/
    # ├── master/
    # │   ├── odoo/
    # │   └── upgrade/
    # ├── 13.0/
    # │   ├── odoo/
    # │   └── upgrade/ -> root/master/upgrade

    # cd into root/13.0/upgrade
    # normalize_path('../odoo')
    # using os.getenv("PWD") : root/13.0/odoo (good, base_directory is root/13.0/upgrade)
    # using os.getcwd() : root/master/odoo (not good, base_directory is root/master/upgrade)

    if relative_to_file:
        base_directory = os.path.dirname(os.path.dirname(os.path.join(base_directory, __file__)))
    abs_path = os.path.join(base_directory, path)
    return os.path.normpath(abs_path)


def run():
    parser = argparse.ArgumentParser(
        """
    Helper to test migration between two versions. THINK TO ADD YOUR SYMLINKS
    Main flow:
    [1.0: checkout source version in addons_path] if given
    1.1: install or restore a template in source version
    1.2: launch test_prepare in source version
    [2.0 checkout target version in addons_path] if given,
    2.1 upgrade database to target version,
    2.2 launch test_check in target version
    """,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30, width=120),
    )

    parser.add_argument(
        "--exec-path",
        help="Path to odoo executable, default to ../odoo/odoo-bin relative to this utility file (upgrade/../odoo/addons)\
                        given path can be relative to working directory",
        default=False,
    )
    parser.add_argument(
        "--addons-path",
        help="Path to addons path to use, default to ../odoo/addons relative to this utility file (upgrade/../odoo/addons)\
                        given path can be relative to working directory\
                        when using checkout options, each addons_path will be the target of a checkout.",
        default=False,
    )

    parser.add_argument(
        "--test-tags",
        default="upgrade",
        help="Allows to define custom partial test-tag list.\
                        Example:\
                        `integrity_case` to only tests IntegrityCase (automatic tag)\
                        `to_fix` to only tests breaking tests (convention for breaking tests to fix)\
                        `to_fix,-/module:TestCase` to remove a specific TestCase from previous example.\
                        Check odoo (>=12.0) help for more details\
                        Method name cannot be given (.test_method) since either .test_prerare or .test_check will be called",
    )
    parser.add_argument(
        "--dry-run", default=False, action="store_true", help="Only log commands without executing anything"
    )

    parser.add_argument(
        "--upgrade-path",
        default=None,
        help="Path to give as upgrade path, usefull if simlink are not present",
    )

    checkout_group = parser.add_argument_group("Checkout", "Checkout mode to switch version")
    checkout_group.add_argument(
        "-c",
        "--checkout",
        metavar="BRANCH",
        help="Odoo source and target versions to checkout. Example `-c 12.0 13.0` to test migration from 12.0 to 13.0\
                BRANCH can be a branch name or commit, and can also be a comma separated list to checkout different version\
                in each addons path.\
                Example: -c 12.0,12.0-my-dev-tri 13.0 --addons-path odoo/addons,enterprise to checkout 12.0-my-dev-tri in \
                source enterprise in enterprise when initiating database",
        default=False,
        nargs=2,
    )

    multiverse_group = parser.add_argument_group(
        """Multiverse
    Example:
     root/
     ├── master/
     │   ├── odoo/
     │   ├── enterprise/
     │   └── upgrade/
     ├── 13.0/
     │   ├── odoo/
     │   ├── enterprise/
     │   └── upgrade/
     ├─── 12.0/
     │   ├── odoo/
     │   ├── enterprise/
     │   └── upgrade/
     ├── ...)
"""
    )

    multiverse_group.add_argument(
        "-m",
        "--multiverse",
        default=False,
        nargs=2,
        metavar="STR",
        help="`pattern replace`, a replace to do in addons absolutes paths to change of verse in a multiverse. \
                Example: `-m /12.0/ /13.0/` for the multiverse example will switch from `root/12.0/odoo/addons` \
                to `root/13.0/odoo/addons` and `root/12.0/enterprise` to `root/13.0/enterprise` \
                Other Example: `-m 12 13` will switch from `root/odoo-12/addons` to `root/odoo-13/addons` \
                and `root/enterprise-12` to `root/enterprise-13`",
    )
    custom_group = parser.add_argument_group("Custom paths")
    custom_group.add_argument(
        "--target-exec-path",
        default=False,
        help="Allow to define exec-path of target version, if multiverse options are not enough",
    )
    custom_group.add_argument(
        "--target-addons-path",
        default=False,
        help="Allow to define addons-path of target version, if multiverse options are not enough",
    )

    database_group = parser.add_argument_group("Database")

    database_group.add_argument(
        "-d",
        "--database",
        default="test_upgrade",
        help="Name of the database to create to test upgrades. Default to `test_upgrade`",
    )
    database_group.add_argument(
        "-i",
        "--init",
        metavar="MODULES",
        default="base",
        help="comma separated list of modules to install (or use --restore)",
    )
    database_group.add_argument(
        "--restore",
        default=False,
        metavar="TEMPLATE",
        help="restore TEMPLATE (a database installed in source version ) instead of installing a new database",
    )
    database_group.add_argument(
        "--auto-drop",
        default=False,
        action="store_true",
        help="Auto drop `database` at the beginning if it already exists. Especially usefull to debug when used with restore",
    )
    database_group.add_argument(
        "--keep-database",
        default=False,
        action="store_true",
        help="Keep existing database and continue without restore or init.",
    )

    logging_group = parser.add_argument_group("Logging")
    logging_group.add_argument("--logfile", default=False, help="Log file to use instead of stdout/stderr")
    logging_group.add_argument(
        "--log-level", default=False, help="odoo log-level to use. See odoo-bin help for more info"
    )

    args = parser.parse_args()

    if args.logfile:
        dirname = os.path.dirname(args.logfile)
        if dirname and not os.path.isdir(dirname):
            os.makedirs(dirname)
        handler = WatchedFileHandler(args.logfile)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

    def die(message):
        _logger.error("%s\n%s", message, parser.format_help())
        parser.format_help()
        sys.exit(1)

    if not (args.checkout or args.multiverse or (args.target_addons_path and args.target_exec_path)):
        die(
            """
You must at least define one of:
--checkout (-c) to automaticaly checkout version Ex: -c 12.0,12.0-my-dev-tri 13.0 (from_odoo,from_enterprise )
`--multiverse from to`: to give a replace pattern to navigate in your multiverse (Ex: `-m 12.0 13.0`)
--target-addons-path and --target-exec-path to define paths where to find odoo-bin and addons path in target version
"""
        )

    if args.multiverse and (args.target_addons_path or args.target_exec_path):
        die("""Defining both multiverse and target-addons-path/target-exec-path makes no sence""")

    if args.restore == args.database:
        die("file to restore and database cannot have the same name, use keep-database instead")

    if args.init != "base" and args.restore:
        die("""Defining both init and restore makes no sence""")

    if not args.exec_path:
        exec_path = normalize_path("../odoo/odoo-bin", True)
    else:
        exec_path = normalize_path(args.exec_path)

    if not args.addons_path:
        addons_path = [normalize_path("../odoo/addons", True)]  # , normalize_path('../enterprise')
    else:
        addons_path = [normalize_path(path) for path in args.addons_path.split(",")]

    target_exec_path = source_exec_path = exec_path
    target_addons_path = source_addons_path = addons_path

    # automatic multiverse management
    if args.multiverse:
        source_multiverse, target_multiverse = args.multiverse
        source_exec_path = source_exec_path.replace(target_multiverse, source_multiverse)
        source_addons_path = [t.replace(target_multiverse, source_multiverse) for t in source_addons_path]
        target_exec_path = source_exec_path.replace(source_multiverse, target_multiverse)
        target_addons_path = [t.replace(source_multiverse, target_multiverse) for t in source_addons_path]

    # manual multiverse management
    if args.target_exec_path:
        target_exec_path = normalize_path(args.target_exec_path)
    if args.target_addons_path:
        target_addons_path = [normalize_path(path) for path in args.target_addons_path.split(",")]
    checkout = False
    if args.checkout:
        checkout = True
        source_checkout, target_checkout = args.checkout and [c.split(",") for c in args.checkout] or (False, False)

        def normalize_checkout(checkout, addons, typename):
            if len(checkout) == 1:
                return checkout * len(addons)
            elif len(checkout) != len(addons):
                die("checkout %s must be same length as addons path, got %s and %s" % (typename, checkout, addons))
            return checkout

        source_checkout = normalize_checkout(source_checkout, source_addons_path, "source")
        target_checkout = normalize_checkout(target_checkout, target_addons_path, "target")

    if "." in args.test_tags:
        die("Defining test-tags method (.method) makes no sense for this script.")

    odoo = Odoo(args.database, args.logfile, args.log_level, args.dry_run, args.upgrade_path)

    need_install = True
    if odoo.db_exists():
        if args.auto_drop:
            odoo.drop_db()
        elif args.keep_database:
            need_install = False
        else:
            _logger.error(
                "Database already exists. Use --auto-drop to drop database %s automaticaly ", odoo.database
            )  # todo add some colors
            sys.exit(1)

    if checkout:
        odoo.checkout(source_checkout, source_addons_path)

    if need_install:
        if args.restore:
            # todo check db exist and version
            odoo.restore_db(args.restore)
        else:
            odoo.run(source_exec_path, source_addons_path, "-i", args.init)

    def _make_tags(method):
        return ",".join(["%s.%s" % (test_tag, method) for test_tag in args.test_tags.split(",")])

    odoo.run(source_exec_path, source_addons_path, "--test-tags", _make_tags("test_prepare"))

    # odoo.dump_db('%s-prepared' % odoo.database)

    if checkout:
        odoo.checkout(target_checkout, target_addons_path)
    odoo.run(target_exec_path, target_addons_path, "-u", "all")
    odoo.run(target_exec_path, target_addons_path, "--test-tags", _make_tags("test_check"))

    # todo drop table ?


if __name__ == "__main__":
    run()
