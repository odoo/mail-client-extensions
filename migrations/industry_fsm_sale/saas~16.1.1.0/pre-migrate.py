# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "industry_fsm_sale.field_service_project_stage_0")
    util.update_record_from_xml(cr, "industry_fsm.fsm_project", force_create=True)
