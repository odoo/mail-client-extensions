# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "planning_self_unassign_days_before", "integer", default=0)
