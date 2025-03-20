import uuid

from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    for table, col in [("pos_config", "access_token"), ("restaurant_table", "identifier")]:
        util.create_column(cr, table, col, "varchar")
        cr.execute(util.format_query(cr, "SELECT id FROM {}", table))
        if cr.rowcount:
            data = {r[0]: uuid.uuid4().hex[:16] for r in cr.fetchall()}
            query = util.format_query(cr, "UPDATE {table} SET {col}=(%s::jsonb)->>(id::text)", table=table, col=col)
            cr.execute(query, [Json(data)])
