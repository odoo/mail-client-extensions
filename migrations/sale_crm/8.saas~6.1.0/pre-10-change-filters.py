# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.update_field_references(cr, 'categ_ids', 'tag_ids',
                                 only_models=('sale.order',))

