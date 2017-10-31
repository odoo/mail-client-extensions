# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'calendar_event', 'res_id', 'int4')
    util.create_column(cr, 'calendar_event', 'res_model_id', 'int4')
    util.create_column(cr, 'calendar_event', 'res_model', 'varchar')
