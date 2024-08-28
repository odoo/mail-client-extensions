from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "account.fr.fec", "l10n_fr.fec.export.wizard")
    util.remove_view(cr, "l10n_fr_account.account_fr_fec_view")
    util.remove_field(cr, "l10n_fr.fec.export.wizard", "fec_data")
