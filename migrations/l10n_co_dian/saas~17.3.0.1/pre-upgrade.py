from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_co_edi_cufe_cude_ref", "varchar")
    util.create_column(cr, "account_move", "l10n_co_dian_state", "varchar")
