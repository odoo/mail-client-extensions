from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant.account_reconcile_model_form_inherit_account_accountant")
