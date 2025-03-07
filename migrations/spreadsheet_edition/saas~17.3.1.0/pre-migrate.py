import re
import sys
import uuid
from concurrent.futures import ProcessPoolExecutor

from psycopg2.extras import execute_batch

from odoo.upgrade import util
from odoo.upgrade.util import json

BATCH_SIZE = 1000
MANY = BATCH_SIZE * util.get_max_workers()


def parse_dimension(dimension):
    values = dimension.split(":")
    if len(values) > 1:
        return {"name": values[0], "granularity": values[1]}
    return {"name": values[0]}


def update_data(query_row):
    revision_id, data = query_row
    data_loaded = json.loads(data)
    for command in data_loaded.get("commands", []):
        if command["type"] == "UPDATE_CELL" and command.get("content"):
            command["content"] = re.sub(r"\bODOO\.PIVOT\(", "PIVOT.VALUE(", command["content"], flags=re.I)
            command["content"] = re.sub(r"\bODOO\.PIVOT\.TABLE\b", "PIVOT", command["content"], flags=re.I)
            command["content"] = re.sub(r"\bODOO\.PIVOT\.HEADER\b", "PIVOT.HEADER", command["content"], flags=re.I)
        elif command["type"] in ["ADD_PIVOT", "UPDATE_PIVOT"]:
            command["pivot"]["measures"] = [{"name": measure} for measure in command["pivot"]["measures"]]
            command["pivot"]["columns"] = [parse_dimension(col) for col in command["pivot"]["colGroupBys"]]
            command["pivot"]["rows"] = [parse_dimension(row) for row in command["pivot"]["rowGroupBys"]]
            del command["pivot"]["colGroupBys"]
            del command["pivot"]["rowGroupBys"]

    return json.dumps(data_loaded), revision_id


def migrate(cr, version):
    name = f"_upgrade_{uuid.uuid4().hex}"
    mod = sys.modules[name] = util.import_script(__file__, name=name)

    query = r"""
    SELECT id, commands
      FROM spreadsheet_revision
     WHERE commands LIKE '%UPDATE\_PIVOT%'
        OR commands LIKE '%ADD\_PIVOT%'
        OR (
                commands LIKE '%UPDATE\_CELL%'
            AND commands LIKE '%ODOO.PIVOT%'
           )
    """
    with ProcessPoolExecutor(max_workers=util.get_max_workers()) as executor, util.named_cursor(cr, BATCH_SIZE) as ncr:
        ncr.execute(query)

        while chunk := ncr.fetchmany(MANY):
            execute_batch(
                cr._obj,
                "UPDATE spreadsheet_revision SET commands=%s WHERE id=%s",
                executor.map(mod.update_data, chunk, chunksize=BATCH_SIZE),
                page_size=BATCH_SIZE,
            )
