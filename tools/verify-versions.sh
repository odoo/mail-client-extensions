#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${DEBUG:-}" ]]; then
    set -x
fi

HERE=$(dirname "$0")
UPGRADEDIR=$(realpath "$HERE/..")

VV_FETCH=1
opt=
while getopts 'hf' opt; do
  case "$opt" in
    h)
        cat <<EOU
    $0 [-f] VERSION

    Options:
        -h           Show this help message.
        -f           Do not fetch reposiories.

    Arguments:
        VERSION      Server version of the script.
                     Can be set via the env variable \$CHECK_VERSION.
                     When the search branch is different than the
                     version (mainly for master branch), use the
                     \`version:branch\` pattern.
EOU
      exit 0
      ;;
   f)
       VV_FETCH=0
      ;;
   *);;
  esac
done

shift $((OPTIND - 1))

if [[ $# != 1 ]]; then
    $0 -h
    exit 1
fi

CHECK_VERSION="$1"

CHECK_BRANCH="${CHECK_VERSION}"
CHECK_VERSION=${CHECK_VERSION%%:*}
CHECK_BRANCH=${CHECK_BRANCH##*:}
CHECK_VERSION=${CHECK_VERSION/-/\~}
CHECK_BRANCH=${CHECK_BRANCH/\~/-}


MATTDIR="$HOME/.local/share/Odoo/upgrade_ci/matt"


grepin () {
    local module blob
    module="$1"
    pushd "$2" >/dev/null
    blob=$(git ls-tree "origin/$CHECK_BRANCH" -- {.,addons,{openerp,odoo}/addons}/"${module}"/__{terp,openerp,manifest}__.py 2>/dev/null | awk '{print $3}')
    if [[ -n $blob ]]; then
        git show "$blob" | python3 -c "import ast,sys;print(ast.literal_eval(sys.stdin.buffer.read().decode()).get('version','1.0'))"
    fi
    popd >/dev/null
}


getversion () {
    local module module_version
    module="$1"

    module_version=$(grepin "$module" "${MATTDIR}/odoo")
    if [[ -z "$module_version" ]]; then
        module_version=$(grepin "$module" "${MATTDIR}/enterprise")
        if [[ -z "$module_version" ]]; then
            module_version=$(grepin "$module" "${MATTDIR}/design-themes")
        fi
    fi
    echo "$module_version"
}

_ver_cmp_1() {
  (( $1 == $2 )) && return 0
  (( $1 > $2 )) && return 1
  (( $1 < $2 )) && return 2
  # This should not be happening
  exit 1
}

ver_cmp() {
  local A B i result
  set +e
  A="${1/saas\~/}"
  B="${2/saas\~/}"
  A=(${A//./ })
  B=(${B//./ })
  i=0
  while (( i < ${#A[@]} )) && (( i < ${#B[@]})); do
    _ver_cmp_1 "${A[i]}" "${B[i]}"
    result=$?
    [[ $result =~ [12] ]] && return $result
    (( ++i ))
  done
  # Which has more, then it is the newer version
  _ver_cmp_1 "${#A[i]}" "${#B[i]}"
  return $?
}


fetch () {
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
}

if [[ $VV_FETCH -eq 1 || ! -d "$MATTDIR" ]]; then
    fetch
fi

pushd "$UPGRADEDIR/migrations" >/dev/null

ec=0
for dir in */"${CHECK_VERSION}".*; do
    if [[ "${dir:0:2}" = "*/" ]]; then
        echo "🤔 No script found for version ${CHECK_VERSION}"
        exit 1
    fi
    module=$(dirname "$dir")
    version=$(basename "$dir")
    shortversion="${version##${CHECK_VERSION}.}"
    expectedversion="$(getversion "$module")"
    if [[ -z "$expectedversion" ]]; then
        echo "💥 module $module not found!" >/dev/stderr
        ec=1
    elif [[ "$shortversion" != "$expectedversion" ]]; then
        ver_cmp "$shortversion" "$expectedversion"
        result=$?
        if [[ $result = 1 ]]; then
            echo "💥 $dir > $expectedversion"
            ec=1
        elif [[ $result = 2 ]]; then
            echo "⚠️  $dir < $expectedversion"
        fi
    fi
done;

exit $ec
