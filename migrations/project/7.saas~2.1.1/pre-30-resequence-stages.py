# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""UPDATE project_task_type
                     SET sequence = sequence + (SELECT -min(s)
                                                  FROM (SELECT min(sequence) - 2 AS s
                                                          FROM project_task_type
                                                         WHERE state != 'draft'
                                                         UNION
                                                         SELECT 0 AS s
                                                        ) AS f)
                   WHERE state != 'draft'
                """)
    cr.execute("UPDATE project_task_type SET sequence = 1 WHERE state = 'draft'")
