# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'pos_config', 'active', 'boolean')
    cr.execute("UPDATE pos_config SET active = (state='active')")

    util.force_noupdate(cr, 'point_of_sale.index', False)
