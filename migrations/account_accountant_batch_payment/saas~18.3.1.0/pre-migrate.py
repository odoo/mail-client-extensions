from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant_batch_payment.view_account_batch_payment_search_bank_rec_widget")
    util.remove_view(cr, "account_accountant_batch_payment.view_account_batch_payment_list_bank_rec_widget")
