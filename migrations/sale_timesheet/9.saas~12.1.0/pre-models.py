# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.column_exists(cr, 'product_template', 'project_id'):
        util.convert_field_to_property(cr, 'product.template', 'project_id',
                                       'many2one', 'project.project')
