from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.reconcile.wizard", "transfer_amount")
    util.remove_field(cr, "account.reconcile.wizard", "transfer_amount_currency")
