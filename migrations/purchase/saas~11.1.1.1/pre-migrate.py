# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'purchase_order', 'user_id', 'int4')
    cr.execute("UPDATE purchase_order SET user_id=create_uid")
