from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.sg.reports.iaf")
