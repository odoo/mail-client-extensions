from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_sa_edi"):
        util.rename_xmlid(
            cr,
            "l10n_sa_edi.view_account_move_reversal_inherit_l10n_sa_edi",
            "l10n_sa.view_account_move_reversal_inherit_l10n_sa",
        )
