from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant_batch_payment.view_bank_rec_widget_form_inherit_batch_payment")

    util.remove_field(cr, "account.batch.payment.rejection", "next_action_todo")
    util.remove_field(cr, "account.batch.payment.rejection", "cancel_action_todo")
    util.remove_field(cr, "bank.rec.widget", "batch_payments_widget")
