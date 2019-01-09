# -*- coding: utf-8 -*-

from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Pack operations were actually created when opening the wizard to move product.
    # now behaviour changed, pack operations are created on Ready stage.

    pickings = util.env(cr)['stock.picking'].search([
        ('state','in', ('assigned','partially_available')),
        ('pack_operation_ids','=', False)]) 
    pickings.do_prepare_partial()
