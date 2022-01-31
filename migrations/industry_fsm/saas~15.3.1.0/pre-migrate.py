# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "industry_fsm.project_task_action_planning_groupby_user_fsm_view_pivot")
    util.remove_record(cr, "industry_fsm.project_task_action_planning_groupby_user_fsm_view_graph")
