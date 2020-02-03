# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # field change type
    util.remove_field(cr, 'hr.recruitment.config.settings', 'module_hr_recruitment_survey')
    util.remove_view(cr, 'hr_recruitment.view_hr_recruitment_configuration')
    cr.execute(
        "DELETE FROM ir_ui_menu_group_rel WHERE menu_id = %s",
        [util.ref(cr, "hr_recruitment.menu_crm_case_categ0_act_job")],
    )
