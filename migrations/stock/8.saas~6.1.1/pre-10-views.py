# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'stock.view_partner_property_form',
                          'stock.view_partner_stock_form')
    util.force_noupdate(cr, 'stock.view_partner_stock_form', False)

    ### sql views (does it count?)

    # as ORM will try to remove size of `stock_move.state` field via ALTER COLUM query we need to
    # drop depending views
    util.drop_depending_views(cr, 'stock_move', 'state')
