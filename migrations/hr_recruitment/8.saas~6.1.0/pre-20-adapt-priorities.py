# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""UPDATE hr_applicant SET priority=
      CASE
        WHEN priority = '1' THEN '0'
        WHEN priority = '2' THEN '0'
        WHEN priority = '3' THEN '1'
        WHEN priority = '4' THEN '3'
        ELSE '0'
      END
    """)
