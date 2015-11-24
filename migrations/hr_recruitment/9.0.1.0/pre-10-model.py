# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'hr.applicant_category', 'hr.applicant.category', rename_table=False)
