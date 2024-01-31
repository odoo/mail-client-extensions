# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.activity.schedule", "plan_date_deadline", "plan_date")
    util.rename_field(cr, "mail.activity.schedule", "plan_assignation_summary", "plan_summary")
    util.remove_field(cr, "mail.activity.plan", "assignation_summary")
    util.remove_field(cr, "mail.tracking.value", "field_groups")
