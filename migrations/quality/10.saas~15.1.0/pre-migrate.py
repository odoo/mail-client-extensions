# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'quality_point', 'sequence', 'int4')
    cr.execute("UPDATE quality_point SET sequence=10")

    util.rename_field(cr, 'stock.picking', 'check_todo', 'quality_check_todo')
