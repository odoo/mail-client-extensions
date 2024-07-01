from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_fr_invoice_addr.account_move_form_l10n_fr_invoice_addr")
