#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def parse_command_line():
    parser = argparse.ArgumentParser(
        description="Link files from the upgrade-util repo into the upgrade repo",
        epilog="Upgrades of versions that do not support --upgrade-path are thereby enabled.",
    )
    parser.add_argument("-m", "--upgrade-dir", help="Local path of the upgrade repository", default="~/src/upgrade")
    parser.add_argument(
        "-u", "--util-dir", help="Local path of the upgrade-util repository", default="~/src/upgrade-util"
    )
    parser.add_argument(
        "-r", "--remove", action="store_true", help="Remove previously created symlinks instead of creating them."
    )
    return parser.parse_args()


def blockinfile(path, mark, block, remove):
    lines = []
    if path.is_file():
        with path.open() as f:
            lines = f.read().splitlines()

    begin = f"# BEGIN BLOCK {mark}"
    end = f"# END BLOCK {mark}"
    head, tail, inhead, intail = [], [], True, False
    for line in lines:
        if line == begin:
            inhead = False
        if inhead:
            head.append(line)
        if intail:
            tail.append(line)
        if line == end:
            intail = True

    with path.open("w") as f:
        f.write("\n".join([*head, *tail] if remove else [*head, begin, *block, end, *tail]))


def main():
    args = parse_command_line()
    upg_dir = Path(args.upgrade_dir).expanduser()
    mig_dir = upg_dir / "migrations"
    src_dir = Path(args.util_dir).expanduser() / "src"

    if not src_dir.exists():
        sys.exit(
            f"ERROR: upgrade-util source '{src_dir}' doesn't exist. "
            f"Please provide the location of your source repositories."
        )

    if not mig_dir.exists():
        sys.exit(
            f"ERROR: upgrade source '{mig_dir}' doesn't exist. Please provide the location of your source repositories."
        )

    if not args.remove and (mig_dir / "util" / "__init__.py").exists():
        logging.info("It seem upgrade-util is already linked in %s. Refreshing.", mig_dir)

    gitignore = []
    for f in src_dir.rglob("*"):
        if not f.is_file() or f.parent.name == "__pycache__" or f.suffix in (".pyc", "pyo"):
            continue
        r = f.relative_to(src_dir)
        td = mig_dir / r.parent
        sl = td / r.name
        if sl.is_symlink():
            sl.unlink()
        if not args.remove:
            td.mkdir(parents=True, exist_ok=True)
            if not sl.exists():
                sl.symlink_to(f)
            gitignore.append(str(sl.relative_to(upg_dir)))

    logging.info("Symlinks have been %s.", "removed" if args.remove else "added")

    gitignore_file = upg_dir / ".git" / "info" / "exclude"
    if gitignore_file.parent.is_dir():
        blockinfile(gitignore_file, "managed by link-upgrade-util", gitignore, args.remove)
        logging.info("Gitignore file %s has been adapted.", gitignore_file)


if __name__ == "__main__":
    main()
