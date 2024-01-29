# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "timesheet_show_rates", "boolean")
    util.create_column(cr, "res_company", "timesheet_show_leaderboard", "boolean")
    util.remove_field(cr, "res.config.settings", "group_timesheet_leaderboard_show_rates")
    util.remove_field(cr, "res.config.settings", "group_use_timesheet_leaderboard")

    cr.execute(
        "SELECT 1 FROM res_groups_implied_rel WHERE gid=%s AND hid=%s",
        [
            util.ref(cr, "base.group_user"),
            util.ref(cr, "sale_timesheet_enterprise.group_timesheet_leaderboard_show_rates"),
        ],
    )
    if cr.rowcount:
        cr.execute("UPDATE res_company SET timesheet_show_rates = true")

    cr.execute(
        "SELECT 1 FROM res_groups_implied_rel WHERE gid=%s AND hid=%s",
        [util.ref(cr, "base.group_user"), util.ref(cr, "sale_timesheet_enterprise.group_use_timesheet_leaderboard")],
    )
    if cr.rowcount:
        cr.execute("UPDATE res_company SET timesheet_show_leaderboard = true")

    util.remove_record(cr, "sale_timesheet_enterprise.group_timesheet_leaderboard_show_rates")
    util.remove_record(cr, "sale_timesheet_enterprise.group_use_timesheet_leaderboard")
