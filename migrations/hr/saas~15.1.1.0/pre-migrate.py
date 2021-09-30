# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_plan_activity_type", "company_id", "int4")
    util.create_column(cr, "hr_plan", "company_id", "int4")
