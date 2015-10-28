# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE product_template SET type='digital' WHERE digital_content=true")
    util.remove_field(cr, 'product.template', 'digital_content')
