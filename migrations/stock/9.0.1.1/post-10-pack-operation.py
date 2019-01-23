# -*- coding: utf-8 -*-

import logging

from openerp.addons.base.maintenance.migrations import util
from openerp.exceptions import UserError

NS = 'openerp.addons.base.maintenance.migrations.base.9.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    # Pack operations were actually created when opening the wizard to move product.
    # now behaviour changed, pack operations are created on Ready stage.

    pickings = util.env(cr)['stock.picking'].search([
        ('state','in', ('assigned','partially_available')),
        ('pack_operation_ids','=', False)])

    for picking in util.iter_browse(util.env(cr)["stock.picking"], pickings.ids, logger=_logger):
        try:
            picking.do_prepare_partial()
        except UserError as e:
            _logger.warning("Cannot prepare partial picking %s: %s" % (picking.name_get()[0], str(e)))
