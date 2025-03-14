from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "l10n_tr_reports.account_reports_tr_statements_menu")])
