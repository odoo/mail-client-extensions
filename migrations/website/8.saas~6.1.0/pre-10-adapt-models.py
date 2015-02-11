# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'website', 'domain', 'varchar')
    cr.execute("UPDATE website SET domain=name")

    # assign root menu to default_website
    cr.execute("""UPDATE website_menu
                     SET website_id=%s
                   WHERE website_id IS NULL
                     AND parent_id IS NULL
               """, [util.ref(cr, 'website.default_website')])
