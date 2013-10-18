# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""UPDATE crm_case_stage
                     SET sequence = sequence + (SELECT -min(s)
                                                  FROM (SELECT min(sequence) - 2 AS s
                                                          FROM crm_case_stage
                                                         WHERE state != 'draft'
                                                         UNION
                                                         SELECT 0 AS s
                                                        ) AS f)
                   WHERE state != 'draft'
                """)
    cr.execute("UPDATE crm_case_stage SET sequence = 1 WHERE state = 'draft'")
