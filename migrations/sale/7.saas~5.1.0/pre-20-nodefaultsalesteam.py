# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Do not let the ORM to create the column "section_id" to avoid setting it default value to
    # the default salesteam of the admin (which is not the correct one)
    util.create_column(cr, 'sale_order', 'section_id', 'int4')
