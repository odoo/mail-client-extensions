# -*- coding: utf-8 -*-


def migrate(cr, version):

    # ==========================================================================
    # Task 2308880: New unicity constraint (name, company_id)
    # ==========================================================================

    cr.execute(
        """
        WITH duplicates AS (
            SELECT company_id,
                   name,
                   ARRAY_AGG(id ORDER BY id) AS ids
              FROM account_followup_followup_line
          GROUP BY company_id, name
            HAVING COUNT(*) > 1
        )
        UPDATE account_followup_followup_line followup_line
           SET name = duplicates.name || ' ' || ARRAY_POSITION(duplicates.ids, followup_line.id)
          FROM duplicates
         WHERE followup_line.id = ANY(duplicates.ids)
        """
    )
