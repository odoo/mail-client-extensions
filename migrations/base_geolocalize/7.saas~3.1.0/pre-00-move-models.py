# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for field in "partner_latitude partner_longitude date_localization".split():
        util.move_field_to_module(cr, 'res.partner', field, 'crm_partner_assign', 'base_geolocalize')

