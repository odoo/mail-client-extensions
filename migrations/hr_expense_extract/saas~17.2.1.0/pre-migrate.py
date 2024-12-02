from odoo.upgrade import util


def migrate(cr, version):
    if not util.module_installed(cr, "account_invoice_extract"):
        util.remove_inherit_from_model(cr, "account.move", "extract.mixin")
