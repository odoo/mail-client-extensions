#!/usr/bin/env bash
set -euo pipefail
T=$(mktemp)
trap 'rm -f "$T"' EXIT
: "${PREFIX:=matt-}"
psql -d postgres -tAF" " -c "\l ${PREFIX}*" | awk '{if($2 == ENVIRON["USER"]) print $1}' > "$T"
S=$(wc -l "$T" | awk '{print $1}')
if [[ $S -eq 0 ]]; then
    echo "🥳 No databases to remove"
    exit 0
fi
echo "🗑  Deleting $S databases"
(while read -r db; do echo "$db"; dropdb "$db"; done < "$T") | pv -betlap -s "$S" >/dev/null
