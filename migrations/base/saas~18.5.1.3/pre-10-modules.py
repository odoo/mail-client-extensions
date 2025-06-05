from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_be_reports_prorata", "l10n_be_reports")
