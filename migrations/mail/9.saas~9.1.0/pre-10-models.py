# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # create column ourself to avoid ORM to set value to 0 on all partners
    util.create_column(cr, 'res_partner', 'message_bounce', 'int4')
