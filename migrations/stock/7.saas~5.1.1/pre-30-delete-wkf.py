from openerp.addons.base.maintenance.migrations import util

# -*- coding: utf-8 -*-
def migrate(cr, version):
    """Delete procurement order wkf """

    util.drop_workflow(cr, 'stock.picking')
