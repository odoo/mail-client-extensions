# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):

    networks = 'twitter facebook github linkedin youtube googleplus'.split()
    for network in networks:
        util.create_column(cr, 'res_company', 'social_' + network, 'varchar')
    cr.execute("""
        UPDATE res_company c
           SET {}
          FROM website w
         WHERE c.id = w.company_id
    """.format(','.join('social_{0} = w.social_{0}'.format(n) for n in networks)))

    for network in networks:
        # field still exists as related.
        util.remove_column(cr, 'website', 'social_' + network)

    util.remove_view(cr, 'website.user_navbar')     # force recreation
