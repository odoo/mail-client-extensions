#!/usr/bin/env bash
set -euo pipefail

: "${DOCKER_IMAGE:=upgrade-ci:1}"

HERE=$(dirname "$0")
UPGRADEDIR=$(realpath "$HERE/..")

DATADIR="$HOME/.local/share/Odoo"
MATTDIR="$DATADIR/upgrade_ci/matt"

# SETUP MATTDIR
mkdir -p "$MATTDIR"

pushd "$MATTDIR" >/dev/null
for repo in odoo enterprise design-themes upgrade-util; do
    if test ! -d "$MATTDIR/$repo"; then
        git clone --bare -q "git@github.com:odoo/${repo}.git" "$repo"
        pushd "$MATTDIR/$repo" >/dev/null
        git config --local --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
        git config --local --add remote.origin.fetch '+refs/pull/*/head:refs/remotes/origin/pr/*'
        popd >/dev/null
    fi
    if [[ "${MATT_FETCH:-1}" = 1 ]]; then
        pushd "$MATTDIR/$repo" >/dev/null
        git -c gc.auto=0 fetch -q
        rm -f gc.log
        git gc --quiet --auto
        git worktree prune
        popd >/dev/null
    fi
done
popd >/dev/null

touch "$TMPDIR/q"

set -x
# run matt via docker
docker run --rm --tty --network=none \
    -v "$UPGRADEDIR:/upgrade" -v "$MATTDIR:/matt" \
    -e TMPDIR=/tmp -v "$TMPDIR/q:/tmp/q" \
    "$DOCKER_IMAGE" /run-matt.sh "$@"
