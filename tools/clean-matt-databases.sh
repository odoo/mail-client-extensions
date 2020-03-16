#!/usr/bin/env bash
set -euo pipefail
T=$(mktemp)
trap 'rm -f "$T"' EXIT
psql -d postgres -tAF" " -c '\l matt-*' | awk '{if($2 == ENVIRON["USER"]) print $1}' > "$T"
S=$(wc -l "$T" | awk '{print $1}')
echo "Deleting $S databases"
(while read -r db; do echo "$db"; dropdb "$db"; done < "$T") | pv -betlap -s "$S" >/dev/null
