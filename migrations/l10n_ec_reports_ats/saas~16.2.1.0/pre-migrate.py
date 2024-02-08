from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_ec.tax.report.ats.handler")
