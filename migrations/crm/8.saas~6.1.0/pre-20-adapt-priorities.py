# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # as ORM will try to remove size of `priority` field via ALTER COLUM query we need to
    # drop depending views
    for v in util.get_depending_views(cr, 'crm_lead', 'priority'):
        cr.execute("DROP VIEW IF EXISTS " + v)

    cr.execute("""UPDATE crm_lead SET priority=
      CASE
        WHEN priority = '0' THEN '1'
        WHEN priority = '2' THEN '0'
        WHEN priority = '3' THEN '2'
        WHEN priority = '4' THEN '3'
        ELSE priority
      END
    """)
