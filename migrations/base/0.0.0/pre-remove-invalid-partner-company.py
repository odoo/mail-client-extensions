def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_partner p
           SET company_id = NULL
          FROM res_company c
         WHERE p.id = c.partner_id
           AND p.company_id != c.id
           AND p.company_id IS NOT NULL
        """
    )
