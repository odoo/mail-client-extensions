# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    types = ['calendar.categ_meet%d' % d for d in range(1, 6)]
    util.delete_unused(cr, *types)
