def migrate(cr, version):
    cr.execute(
        """
        WITH agg_data AS (
            SELECT p.id
              FROM onboarding_progress AS p
              JOIN onboarding_onboarding_onboarding_onboarding_step_rel AS rel
                ON rel.onboarding_onboarding_id = p.onboarding_id
              JOIN onboarding_onboarding_step AS s
                ON rel.onboarding_onboarding_step_id = s.id
          GROUP BY p.id,
                   p.company_id,
                   p.onboarding_id
            HAVING (p.company_id IS NULL) = BOOL_OR(s.is_per_company)
        )
        DELETE FROM onboarding_progress AS p
              USING agg_data
              WHERE p.id = agg_data.id
        """
    )
