# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'res.partner', 'commercial_partner_country_id')
    util.remove_field(cr, 'res.group', 'is_portal')
