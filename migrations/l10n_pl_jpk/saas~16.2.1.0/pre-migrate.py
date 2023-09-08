from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "l10n_pl_tax_office", "l10n_pl_jpk.l10n_pl_tax_office")
