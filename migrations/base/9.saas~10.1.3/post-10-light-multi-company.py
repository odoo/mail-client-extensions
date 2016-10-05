# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.split_group(cr, 'base.group_light_multi_company', 'base.group_multi_company')
