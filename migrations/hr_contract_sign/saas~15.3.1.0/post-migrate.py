# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.plan.activity.type", ["employee_role_id"])
