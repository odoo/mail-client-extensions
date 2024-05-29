from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "l10n_hu_edi_actionable_errors")
