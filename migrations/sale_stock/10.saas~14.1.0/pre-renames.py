# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces('sale{,_stock}.group_display_incoterm'))
