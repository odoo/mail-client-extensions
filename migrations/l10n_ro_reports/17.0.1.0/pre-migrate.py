from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n_ro.report.handler")
