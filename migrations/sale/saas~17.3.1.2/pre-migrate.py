from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale.sale_order_view_form")
    util.remove_record(cr, "sale.onboarding_onboarding_sale_quotation")
    util.remove_record(cr, "sale.onboarding_onboarding_step_sale_order_confirmation")
    util.remove_record(cr, "sale.onboarding_onboarding_step_sample_quotation")
