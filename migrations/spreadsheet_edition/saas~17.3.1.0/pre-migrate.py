import collections
import re
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context

from odoo.sql_db import db_connect

from odoo.upgrade import util
from odoo.upgrade.util import json


def parse_dimension(dimension):
    values = dimension.split(":")
    if len(values) > 1:
        return {"name": values[0], "granularity": values[1]}
    return {"name": values[0]}


def update_command(id):
    cr = update_command.cr
    cr.execute("SELECT commands FROM spreadsheet_revision WHERE id = %s", [id])
    data_loaded = json.loads(cr.fetchone()[0])
    changed = False
    for command in data_loaded.get("commands", []):
        if command["type"] == "UPDATE_CELL" and command.get("content"):
            command["content"] = re.sub(r"\bODOO\.PIVOT\(", "PIVOT.VALUE(", command["content"], flags=re.I)
            command["content"] = re.sub(r"\bODOO\.PIVOT\.TABLE\b", "PIVOT", command["content"], flags=re.I)
            command["content"] = re.sub(r"\bODOO\.PIVOT\.HEADER\b", "PIVOT.HEADER", command["content"], flags=re.I)
            changed = True
        elif command["type"] in ["ADD_PIVOT", "UPDATE_PIVOT"]:
            command["pivot"]["measures"] = [{"name": measure} for measure in command["pivot"]["measures"]]
            command["pivot"]["columns"] = [parse_dimension(col) for col in command["pivot"]["colGroupBys"]]
            command["pivot"]["rows"] = [parse_dimension(row) for row in command["pivot"]["rowGroupBys"]]
            del command["pivot"]["colGroupBys"]
            del command["pivot"]["rowGroupBys"]
            changed = True
    if changed:
        cr.execute("UPDATE spreadsheet_revision SET commands = %s WHERE id = %s", [json.dumps(data_loaded), id])


def init_worker(dbname):
    conn = db_connect(dbname)
    update_command.cr = conn.cursor()
    update_command.cr._cnx.autocommit = True


def migrate(cr, version):
    cr.commit()
    cr.execute(
        r"""
        SELECT id
          FROM spreadsheet_revision
         WHERE commands LIKE '%UPDATE\_PIVOT%'
            OR commands LIKE '%ADD\_PIVOT%'
            OR (
                    commands LIKE '%UPDATE\_CELL%'
                AND commands LIKE '%ODOO.PIVOT%'
               )
        """
    )
    with ProcessPoolExecutor(
        max_workers=util.get_max_workers(),
        mp_context=get_context("fork"),
        initializer=util.make_pickleable_callback(init_worker),
        initargs=[cr.dbname],
    ) as executor:
        while ids := cr.fetchmany(50000):
            # consume results to propagate workers' exceptions
            collections.deque(
                executor.map(util.make_pickleable_callback(update_command), (id for (id,) in ids)), maxlen=0
            )
    cr.commit()
