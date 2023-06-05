def migrate(cr, version):
    # We try to identify companies in the database that are "associations" by looking for AMLs using a 73* account
    # (these are only used by associations). These companies are changed to use the `be_asso` CoA, while the other
    # Belgian companies are changed to use the `be_comp` CoA.
    cr.execute(
        """
        WITH associations AS (
          SELECT c.id
            FROM res_company c
            JOIN account_move_line l
              ON l.company_id = c.id
            JOIN account_account a
              ON a.id = l.account_id
           WHERE c.chart_template = 'be'
             AND a.code like '73%'
        GROUP BY c.id
        )
        UPDATE res_company
           SET chart_template = 'be_asso'
          FROM associations
         WHERE res_company.id = associations.id
        """
    )
    cr.execute("UPDATE res_company SET chart_template = 'be_comp' WHERE chart_template = 'be'")
