# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # field change type
    util.remove_field(cr, 'hr.recruitment.config.settings', 'module_hr_recruitment_survey')
    util.remove_view(cr, 'hr_recruitment.view_hr_recruitment_configuration')
