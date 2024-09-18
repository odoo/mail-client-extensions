from odoo.upgrade import util


def migrate(cr, version):
    reason_3 = util.ref(cr, "sale_subscription.close_reason_3")
    end_of_contract = util.ref(cr, "sale_subscription.close_reason_end_of_contract")
    if reason_3 and end_of_contract:
        util.replace_record_references_batch(
            cr, {reason_3: end_of_contract}, "sale.order.close.reason", replace_xmlid=False
        )
        util.remove_record(cr, "sale_subscription.close_reason_3")

    # Remove SaleOrderAlert and its views. From now on, automations will be made in Studio.
    util.remove_field(cr, "base.automation", "is_sale_order_alert")
    util.remove_model(cr, "sale.order.alert")
    util.remove_view(cr, "sale_subscription.sale_subscription_base_automation_form")
    util.remove_menus(cr, [util.ref(cr, "sale_subscription.menu_sale_subscription_alert")])

    # Remove the subscription health field from sale orders and reports.
    util.remove_field(cr, "sale.order", "health")
    util.remove_field(cr, "sale.order.log.report", "health")
    util.remove_field(cr, "sale.subscription.report", "health")
