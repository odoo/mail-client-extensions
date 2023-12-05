def migrate(cr, version):
    cr.execute(
        """
        WITH cte_max AS (
              SELECT m.res_id,
                     MAX(m.create_date) AS last_stage_change
                FROM mail_message m
                JOIN mail_message_subtype ms
                  ON ms.id = m.subtype_id
               WHERE m.model = 'maintenance.request'
                 AND ms.name->>'en_US' = 'Status Changed'
            GROUP BY m.res_id
            )
              UPDATE maintenance_request r
                 SET close_date = COALESCE(cte.last_stage_change, r.write_date)
                FROM maintenance_request r1
                JOIN maintenance_stage s
                  ON r1.stage_id = s.id
           LEFT JOIN cte_max cte
                  ON cte.res_id = r1.id
               WHERE r.close_date IS NULL
                 AND r.id = r1.id
                 AND s.done = true
        """
    )
