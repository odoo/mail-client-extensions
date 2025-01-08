from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_supplierinfo", "discount", "float8", default=0)
    cr.execute(
        "SELECT 1 FROM res_groups_implied_rel WHERE gid = %s AND hid = %s",
        [util.ref(cr, "base.group_user"), util.ref(cr, "product.group_product_pricelist")],
    )
    if not cr.rowcount:
        cr.execute("UPDATE product_pricelist SET active = False WHERE active")
