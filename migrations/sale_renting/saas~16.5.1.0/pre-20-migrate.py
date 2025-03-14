from odoo.upgrade import util


def migrate(cr, version):
    # move internal note to log note for rental orders before removing the field.
    cr.execute(
        """
           SELECT id, internal_note
             FROM sale_order so
            WHERE is_rental_order = true
              AND internal_note IS NOT NULL
        """
    )
    values = dict(cr.fetchall())

    for so in util.iter_browse(util.env(cr)["sale.order"], values.keys()):
        so.message_post(body=values[so.id])

    if not util.module_installed(cr, "sale_subscription"):
        util.remove_field(cr, "sale.order", "internal_note")
    # remove stuff coming from the merge sale_temporal -> sale_renting
    util.remove_view(cr, "sale_renting.sale_subscription_order_view_form")
    util.remove_view(cr, "sale_renting.product_template_form_view_pricing")
    util.remove_view(cr, "sale_renting.product_template_tree_view")
    util.remove_view(cr, "sale_renting.product_template_kanban_view")

    util.remove_field(cr, "sale.order.line", "temporal_type")
    util.remove_field(cr, "product.template", "is_temporal")
    util.remove_field(cr, "sale.temporal.recurrence", "temporal_unit_display")

    util.rename_xmlid(cr, "sale_renting.sale_temporal_product_pricing_tree", "sale_renting.product_pricing_tree")
