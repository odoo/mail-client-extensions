from odoo.upgrade import util


def migrate(cr, version):
    # computed stored field from `l10n_ro_efactura`; don't recompute it
    util.create_column(cr, "account_move", "l10n_ro_edi_state", "varchar")
    util.remove_field(cr, "account.move.send", "l10n_ro_edi_warnings")
