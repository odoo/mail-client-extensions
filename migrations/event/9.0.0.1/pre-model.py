# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'back innerleft innerright'.split():
        util.move_field_to_module(cr, 'event.event', 'badge_' + f, 'event_sale', 'event')
