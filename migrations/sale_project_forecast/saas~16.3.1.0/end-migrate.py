from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT id
          FROM product_template
         WHERE planning_enabled = TRUE
        """
    util.recompute_fields(cr, "product.template", ["planning_enabled"], query=query)
