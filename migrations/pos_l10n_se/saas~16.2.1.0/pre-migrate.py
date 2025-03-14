from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "pos_l10n_se.menu_report_daily_details")])
    util.remove_view(cr, "pos_l10n_se.view_pos_details_wizard")
    util.remove_record(cr, "pos_l10n_se.pos_daily_report")
    util.remove_record(cr, "pos_l10n_se.action_report_pos_daily_reports")
    util.remove_model(cr, "pos.daily.reports.wizard")
