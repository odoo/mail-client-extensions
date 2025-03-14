from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "pos_category_product_template_rel", "pos_category", "product_template")
    cr.execute(
        """
            INSERT INTO pos_category_product_template_rel
                        (product_template_id, pos_category_id)
            SELECT id,
                   pos_categ_id
            FROM   product_template
            WHERE  pos_categ_id IS NOT NULL
        """
    )
    util.update_field_usage(cr, "product.template", "pos_categ_id", "pos_categ_ids")
    util.remove_field(cr, "product.template", "pos_categ_id")
    util.remove_field(cr, "report.pos.order", "pos_categ_id")
