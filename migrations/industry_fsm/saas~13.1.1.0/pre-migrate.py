# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm.project_task_view_form")
    util.remove_view(cr, "industry_fsm.project_task_view_form_fsm_quotation")

    util.force_noupdate(cr, "industry_fsm.view_task_form2_inherit", False)
    util.force_noupdate(cr, "industry_fsm.res_config_settings_view_form", False)

    util.remove_view(cr, "industry_fsm.view_form2")
    util.remove_view(cr, "industry_fsm.view_sale_service_inherit_form2")
    util.remove_view(cr, "industry_fsm.project_project_view_form_simplified_inherit")
