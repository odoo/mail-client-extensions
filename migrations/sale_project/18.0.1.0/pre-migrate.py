from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "reinvoiced_sale_order_id", "int4")

    # Set field value based on sale_line_id associated to project.
    cr.execute(
        """
        UPDATE project_project pp
           SET reinvoiced_sale_order_id = sol.order_id
          FROM sale_order_line sol
         WHERE pp.sale_line_id = sol.id
           AND pp.reinvoiced_sale_order_id IS NULL;
        """
    )
