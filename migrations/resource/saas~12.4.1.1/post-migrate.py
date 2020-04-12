# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "resource.resource_calendar_leaves_rule_group_user_create", False)
    util.update_record_from_xml(cr, "resource.resource_calendar_leaves_rule_group_user_modify", False)
