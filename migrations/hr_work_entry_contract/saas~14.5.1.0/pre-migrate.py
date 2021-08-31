# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "create.company.global.time.off")
    util.remove_view(cr, "hr_work_entry_contract.resource_calendar_view_form")
