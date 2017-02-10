# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'theme_loftspace_sale.products', False)
