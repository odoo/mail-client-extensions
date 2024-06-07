import json
import re

from odoo.upgrade import util

BATCH_SIZE = 1000


def migrate(cr, version):
    def update_data(query_row):
        revision_id, data = query_row
        data_loaded = json.loads(data)
        for command in data_loaded.get("commands", []):
            if command["type"] == "UPDATE_CELL" and command.get("content"):
                command["content"] = re.sub(r"\bODOO\.PIVOT\(", "PIVOT.VALUE(", command["content"], flags=re.I)
                command["content"] = re.sub(r"\bODOO\.PIVOT\.TABLE\b", "PIVOT", command["content"], flags=re.I)
                command["content"] = re.sub(r"\bODOO\.PIVOT\.HEADER\b", "PIVOT.HEADER", command["content"], flags=re.I)
            elif command["type"] == "ADD_PIVOT":
                command["pivot"]["measures"] = [{"name": measure} for measure in command["pivot"]["measures"]]
                command["pivot"]["colGroupBys"] = [parse_dimension(col) for col in command["pivot"]["colGroupBys"]]
                command["pivot"]["rowGroupBys"] = [parse_dimension(row) for row in command["pivot"]["rowGroupBys"]]
        cr.execute(
            """
            UPDATE spreadsheet_revision
            SET commands=%s
            WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )

    query = r"""
    SELECT id, commands
      FROM spreadsheet_revision
     WHERE commands LIKE '%UPDATE\_CELL%'
        OR commands LIKE '%ADD\_PIVOT%'
    """
    with util.named_cursor(cr, BATCH_SIZE) as ncr:
        ncr.execute(query)

        for query_row in ncr:
            update_data(query_row)


def parse_dimension(dimension):
    values = dimension.split(":")
    if len(values) > 1:
        return {"name": values[0], "granularity": values[1]}
    return {"name": values[0]}
