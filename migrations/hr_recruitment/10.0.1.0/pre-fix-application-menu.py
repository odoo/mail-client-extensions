# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        "UPDATE ir_ui_menu SET action = NULL WHERE id = %s",
        [util.ref(cr, "hr_recruitment.menu_crm_case_categ0_act_job")],
    )
