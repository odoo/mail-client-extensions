# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_plan_activity_type", "deadline_type", "varchar", default="default")
    util.create_column(cr, "hr_plan_activity_type", "deadline_days", "int4", default=0)
    util.create_column(cr, "hr_plan_activity_type", "company_id", "int4")

    util.create_column(cr, "hr_plan", "plan_type", "varchar", default="onboarding")
    util.create_column(cr, "hr_plan", "trigger", "varchar", default="manual")
    util.create_column(cr, "hr_plan", "company_id", "int4")
