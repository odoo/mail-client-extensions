# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""UPDATE project_task
                     SET priority = CASE WHEN priority='2' THEN '1' ELSE '0' END
               """)
