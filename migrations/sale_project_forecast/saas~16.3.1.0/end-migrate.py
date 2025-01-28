from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id
          FROM product_template
         WHERE planning_enabled = TRUE
        """
    )
    ids = [x[0] for x in cr.fetchall()]
    util.recompute_fields(cr, "product.template", ["planning_enabled"], ids=ids)
