from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale.sale_order_view_form")
    util.remove_record(cr, "sale.onboarding_onboarding_sale_quotation")
    util.remove_record(cr, "sale.onboarding_onboarding_step_sale_order_confirmation")
    util.remove_record(cr, "sale.onboarding_onboarding_step_sample_quotation")
    util.rename_field(cr, "product.document", "attached_on", "attached_on_sale")
    if util.module_installed(cr, "sale_project"):
        util.move_field_to_module(cr, "product.template", "service_tracking", "sale_project", "sale")
        util.explode_execute(
            cr,
            """
            UPDATE product_template
               SET service_tracking = 'no'
             WHERE service_tracking IS NULL
            """,
            table="product_template",
        )
    else:
        util.create_column(cr, "product_template", "service_tracking", "varchar", default="no")
