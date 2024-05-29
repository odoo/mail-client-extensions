from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "l10n_br_edi_warning")
