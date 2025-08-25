import uuid

from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr,
        "pos.order.line",
        "note",
        "pos_restaurant",
        "point_of_sale",
    )
    if util.create_column(cr, "pos_config", "access_token", "varchar"):
        cr.execute("SELECT id FROM pos_config")
        access_token_map = {id_: str(uuid.uuid4().hex[:16]) for (id_,) in cr.fetchall()}
        util.bulk_update_table(cr, "pos_config", "access_token", access_token_map)
