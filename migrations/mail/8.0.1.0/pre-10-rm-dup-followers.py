# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""DELETE FROM mail_followers
                        WHERE id IN (SELECT unnest(x[2:array_upper(x, 1)])
                                       FROM (SELECT array_agg(id) x
                                               FROM mail_followers
                                           GROUP BY res_model, res_id, partner_id
                                             HAVING count(id) > 1
                                            ) t
                                    )
               """)
