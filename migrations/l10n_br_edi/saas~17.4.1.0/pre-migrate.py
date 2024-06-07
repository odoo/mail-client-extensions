from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "l10n_br_edi_warning")
    util.remove_view(cr, "l10n_br_edi.view_move_form")
    util.remove_view(cr, "l10n_br_edi.l10n_br_edi_invoice_update_form")
