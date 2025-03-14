from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_us_reports.check.register")
