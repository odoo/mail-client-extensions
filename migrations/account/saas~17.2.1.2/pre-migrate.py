from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account.account_payment_term_form")
    util.rename_xmlid(cr, "account.account_payment_term_advance", "account.account_payment_term_90days_on_the_10th")
