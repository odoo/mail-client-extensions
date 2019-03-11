# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for action in {"_order", "_confirm", "_cancel", ""}:
        util.remove_record(cr, "lunch.lunch_order_line_action" + action)

    util.remove_view(cr, "lunch.report_lunch_order")
    util.remove_record(cr, "lunch.action_report_lunch_order")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("lunch.lunch_order{_line,}_rule_delete"))

    util.remove_view(cr, "lunch.view_lunch_alert_kanban")
    cr.execute("UPDATE ir_act_window SET help = NULL WHERE id = %s", [util.ref(cr, "lunch.lunch_alert_action")])

    util.remove_view(cr, "lunch.lunch_cashmove_view_search_2")
    util.remove_view(cr, "lunch.lunch_cashmove_view_tree_2")

    util.remove_record(cr, "lunch.lunch_cashmove_action_account")
    util.remove_record(cr, "lunch.lunch_cashmove_action_control_accounts")

    for v in {"search", "tree", "kanban"}:
        util.remove_view(cr, "lunch.lunch_order_line_view_" + v)

    util.rename_xmlid(cr, *eb("lunch.lunch_order{_line,}_action_by_supplier"))
    util.rename_xmlid(cr, *eb("lunch.lunch_order{_line,}_action_control_suppliers"))
