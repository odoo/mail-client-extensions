def migrate(cr, version):
    query = """
      UPDATE ir_model_data d
         SET name = concat(c.id, '_p10058')
        FROM res_company c
        JOIN res_country n
          ON n.id = c.account_fiscal_country_id
       WHERE d.model = 'account.account'
         AND d.name = concat(c.id, '_p10054')
         AND n.code = 'IN'
    """
    cr.execute(query)
