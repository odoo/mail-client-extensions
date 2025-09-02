from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("17.0"):
        util.explode_execute(
            cr,
            """
            UPDATE product_product p
               SET write_date = t.write_date
              FROM product_template t
             WHERE p.product_tmpl_id = t.id
               AND t.write_date > p.write_date
            """,
            table="product_product",
            alias="p",
        )
