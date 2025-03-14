from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "locked", "boolean")

    util.explode_execute(
        cr,
        "UPDATE sale_order SET state = 'sale', locked = true WHERE state = 'done'",
        table="sale_order",
    )
    util.change_field_selection_values(cr, "sale.order", "state", {"done": "sale"})
    util.change_field_selection_values(cr, "sale.order.line", "state", {"done": "sale"})
    util.remove_view(cr, "sale.view_sales_order_auto_done_setting")

    util.remove_view(cr, "sale.sale_quotation_onboarding_panel")
    util.remove_view(cr, "sale.sale_onboarding_sample_quotation_step")
    util.remove_view(cr, "sale.sale_onboarding_order_confirmation_step")
    util.remove_view(cr, "sale.onboarding_quotation_layout_step")
    util.remove_record(cr, "sale.action_open_sale_payment_provider_onboarding_wizard")
