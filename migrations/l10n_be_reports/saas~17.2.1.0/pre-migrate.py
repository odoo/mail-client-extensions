from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "l10n_be_reports.menu_action_create_325_form")])
