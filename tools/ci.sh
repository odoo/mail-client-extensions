#!/usr/bin/env bash
set -euo pipefail

HERE=$(dirname "$0")
UPGRADEDIR=$(realpath "$HERE/..")

DATADIR="$HOME/Library/Application Support/Odoo"
if test ! -d "$DATADIR"; then
    DATADIR="$HOME/.local/share/Odoo"
fi

MATTDIR="$DATADIR/upgrade_ci/matt"

# SETUP MATTDIR
mkdir -p "$MATTDIR"

pushd "$MATTDIR" >/dev/null
for repo in odoo enterprise design-themes; do
    if test ! -d "$MATTDIR/$repo"; then
        git clone --bare -q "git@github.com:odoo/${repo}.git" "$repo"
        pushd "$MATTDIR/$repo" >/dev/null
        git config --local --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
        git config --local --add remote.origin.fetch '+refs/pull/*/head:refs/remotes/origin/pr/*'
    else
        pushd "$MATTDIR/$repo" >/dev/null
    fi
    git -c gc.auto=0 fetch -q
    rm -f gc.log
    git gc --quiet --auto
    git worktree prune
    popd >/dev/null
done
popd >/dev/null

set -x
# run matt via docker
docker run --tty --network=none -v "$UPGRADEDIR:/upgrade" -v "$MATTDIR:/matt" upgrade-ci:1 /run-matt.sh "$@"
