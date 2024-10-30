from odoo.upgrade import util


def migrate(cr, version):
    reason_3 = util.ref(cr, "sale_subscription.close_reason_3")
    end_of_contract = util.ref(cr, "sale_subscription.close_reason_end_of_contract")
    if reason_3 and end_of_contract:
        util.replace_record_references_batch(
            cr, {reason_3: end_of_contract}, "sale.order.close.reason", replace_xmlid=False
        )
        util.remove_record(cr, "sale_subscription.close_reason_3")
