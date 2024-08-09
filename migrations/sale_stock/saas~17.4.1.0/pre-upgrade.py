from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr, "sale_order_line", "warehouse_id", "int4", fk_table="stock_warehouse", on_delete_action="SET NULL"
    )
