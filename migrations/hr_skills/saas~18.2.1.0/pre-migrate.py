def migrate(cr, version):
    cr.execute(
        """
        WITH to_delete AS (
            SELECT hs_type.id
              FROM hr_skill_type hs_type
         LEFT JOIN hr_skill hs
                ON hs.skill_type_id = hs_type.id
         LEFT JOIN hr_skill_level hs_level
                ON hs_level.skill_type_id = hs_type.id
             WHERE hs IS NULL
                OR hs_level IS NULL
             GROUP BY 1
        )
        DELETE FROM hr_skill_type
              USING to_delete
              WHERE to_delete.id = hr_skill_type.id
        """
    )
