from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.partner", "l10n_cl_activity_description", "l10n_cl_edi", "l10n_cl")
    util.move_field_to_module(cr, "res.company", "l10n_cl_activity_description", "l10n_cl_edi", "l10n_cl")  # Not stored
    util.remove_menus(cr, [util.ref(cr, "l10n_cl.account_reports_cl_statements_menu")])
