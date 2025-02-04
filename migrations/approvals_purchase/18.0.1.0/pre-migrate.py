from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr, "approval_product_line", "seller_id", "int4", fk_table="product_supplierinfo", on_delete_action="SET NULL"
    )
