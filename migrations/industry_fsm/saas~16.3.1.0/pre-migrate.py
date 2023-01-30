# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.task", "is_task_phone_update", "industry_fsm_sale", "industry_fsm")
