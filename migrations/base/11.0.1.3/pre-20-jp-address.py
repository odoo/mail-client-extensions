# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE res_country
           SET address_format='%%(zip)s\n%%(state_name)s %%(city)s\n%%(street)s\n%%(street2)s\n%%(country_name)s'
         WHERE id=%s
    """, [util.ref(cr, 'base.jp')])
