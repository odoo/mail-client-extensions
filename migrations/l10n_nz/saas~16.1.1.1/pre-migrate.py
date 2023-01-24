from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_nz.tax_group_100000000", "l10n_nz.tax_group_100")
