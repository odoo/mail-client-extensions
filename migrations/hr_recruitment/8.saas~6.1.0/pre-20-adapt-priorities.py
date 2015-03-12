# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_depending_views(cr, 'hr_applicant', 'priority')

    cr.execute("""UPDATE hr_applicant SET priority=
      CASE
        WHEN priority = '1' THEN '0'
        WHEN priority = '2' THEN '0'
        WHEN priority = '3' THEN '1'
        WHEN priority = '4' THEN '3'
        ELSE '0'
      END
    """)
