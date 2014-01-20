# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    deps = ('hr_recruitment', 'document')
    util.force_install_module(cr, 'hr_applicant_document', if_installed=deps)
