# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("planning.planning_view_search{,_base}"))
    util.remove_record(cr, "planning.planning_action_my_planning_view_pivot")
    util.remove_record(cr, "planning.planning_action_my_planning_view_graph")
