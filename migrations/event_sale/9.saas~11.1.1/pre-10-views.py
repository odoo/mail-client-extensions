# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'event_sale.event_order_line',
                      'event_sale.view_sale_order_form_inherit_event')
