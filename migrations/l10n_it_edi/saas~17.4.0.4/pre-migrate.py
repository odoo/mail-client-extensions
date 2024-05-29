from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "l10n_it_edi_warning_message")
    util.remove_field(cr, "account.move.send", "l10n_it_edi_actionable_errors")
