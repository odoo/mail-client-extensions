# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.module_installed(cr, 'hr_attendance'):
        util.rename_xmlid(cr, *util.expand_braces('{hr,hr_attendance}.group_hr_attendance'))
    else:
        util.remove_record(cr, 'hr.group_hr_attendance')
