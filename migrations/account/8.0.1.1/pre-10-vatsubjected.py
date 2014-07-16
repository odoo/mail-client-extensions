# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'res.partner', 'vat_subjected', 'base_vat', 'account')
