from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "l10n_ke_edi_warning_message")
    util.remove_view(cr, "l10n_ke_edi_tremol.account_move_send_form_inherit_l10n_ke_edi_tremol")
