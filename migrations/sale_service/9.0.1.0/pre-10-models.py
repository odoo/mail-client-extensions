# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE product_template SET track_service='task' WHERE auto_create_task")
    util.remove_field(cr, 'product.template', 'auto_create_task')
