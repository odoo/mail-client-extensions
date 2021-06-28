# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version, module="sale_payment"):
    util.create_m2m(
        cr, "sale_order_transaction_rel", "payment_transaction", "sale_order", "transaction_id", "sale_order_id"
    )
    if util.column_exists(cr, "payment_transaction", "sale_order_id"):
        cr.execute(
            """
            INSERT INTO sale_order_transaction_rel(transaction_id, sale_order_id)
                 SELECT pt.id, pt.sale_order_id
                   FROM payment_transaction pt
                   JOIN sale_order so ON so.id = pt.sale_order_id
        """
        )

    util.remove_field(cr, "payment.transaction", "sale_order_id")
    util.remove_field(cr, "payment.transaction", "so_state")

    util.rename_field(cr, "sale.order", "payment_tx_ids", "transaction_ids")
    util.remove_field(cr, "sale.order", "payment_tx_id")
    util.remove_field(cr, "sale.order", "payment_acquirer_id")
    util.remove_field(cr, "sale.order", "payment_transaction_count")

    for state in {"pending", "authorized"}:
        util.remove_field(cr, "crm.team", "{}_payment_transactions_count".format(state))
        util.remove_field(cr, "crm.team", "{}_payment_transactions_amount".format(state))
        util.remove_record(cr, "{}.payment_transaction_action_{}".format(module, state))

    util.remove_view(cr, module + ".sale_order_view_form")
    util.remove_view(cr, module + ".payment_confirmation_status")
    util.remove_view(cr, module + ".crm_team_salesteams_view_kanban_inherit_website_portal_sale")
