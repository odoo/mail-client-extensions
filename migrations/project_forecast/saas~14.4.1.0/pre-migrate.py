# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "planning.planning_rule_internal_user_read", from_module="planning")
    util.update_record_from_xml(cr, "planning.planning_rule_user_is_published", from_module="planning")
    util.remove_view(cr, "project_forecast.planning_view_form_in_gantt")
    util.remove_field(cr, "planning.slot", "is_private_project")
