# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.task.type", "legend_priority")
    util.remove_record(cr, "project.access_account_analytic_account_portal")

    util.move_field_to_module(cr, "project.task", "partner_city", "industry_fsm", "project")
