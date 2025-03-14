from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_es.sii.account.tax.mixin")
