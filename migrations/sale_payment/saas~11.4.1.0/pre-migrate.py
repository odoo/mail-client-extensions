# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_m2m(
        cr, "sale_order_transaction_rel",
        "payment_transaction", "sale_order",
        "transaction_id", "sale_order_id"
    )
    cr.execute("""
        INSERT INTO sale_order_transaction_rel(transaction_id, sale_order_id)
             SELECT id, sale_order_id
               FROM payment_transaction
              WHERE sale_order_id IS NOT NULL
    """)

    util.remove_field(cr, "payment.transaction", "sale_order_id")
    util.remove_field(cr, "payment.transaction", "so_state")

    util.rename_field(cr, "sale.order", "payment_tx_ids", "transaction_ids")
    util.remove_field(cr, "sale.order", "payment_tx_id")
    util.remove_field(cr, "sale.order", "payment_acquirer_id")
    util.remove_field(cr, "sale.order", "payment_transaction_count")

    for state in {"pending", "authorized"}:
        util.remove_field(cr, "crm.team", "{}_payment_transactions_count".format(state))
        util.remove_field(cr, "crm.team", "{}_payment_transactions_amount".format(state))
        util.remove_record(cr, "sale_payment.payment_transaction_action_{}".format(state))

    util.remove_view(cr, "sale_payment.sale_order_view_form")
    util.remove_view(cr, "sale_payment.payment_confirmation_status")
    util.remove_view(cr, "sale_payment.crm_team_salesteams_view_kanban_inherit_website_portal_sale")
