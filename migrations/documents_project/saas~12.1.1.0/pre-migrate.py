# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, 'res.company', 'dms_project_settings', 'documents_project_settings')
    util.rename_field(cr, 'res.config.settings', 'dms_project_settings', 'documents_project_settings')
