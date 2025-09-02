from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~16.2"):
        _clean_inactive_taxes(cr)


def _clean_inactive_taxes(cr):
    # Rename and remove xmlid from inactive taxes that fail repartition line validations
    # those will be recreated with the correct values if the xmlid is standard.
    # The validation checks that there is the same number of invoice repartition lines
    # and refund repartition lines, and that the two set of lines match exactly
    # when ordered by their sequence and id.
    cr.execute(
        """
  WITH bad_taxes AS (
              SELECT t.id
               FROM account_tax t
               JOIN ir_model_data d
                 ON d.model = 'account.tax'
                AND d.res_id = t.id
          LEFT JOIN account_tax_repartition_line il
                 ON il.tax_id = t.id
                AND il.document_type = 'invoice'
          LEFT JOIN account_tax_repartition_line rl
                 ON rl.tax_id = t.id
                AND rl.document_type = 'refund'
              WHERE NOT t.active
           GROUP BY t.id
             HAVING (
                    ARRAY_AGG(il.repartition_type ORDER BY il.sequence,il.id)
                    IS DISTINCT FROM
                    ARRAY_AGG(rl.repartition_type ORDER BY rl.sequence,rl.id)
                 OR ARRAY_AGG(il.factor_percent ORDER BY il.sequence,il.id)
                    IS DISTINCT FROM
                    ARRAY_AGG(rl.factor_percent ORDER BY rl.sequence,rl.id)
                    )
             ),

 renamed_taxes AS (
           UPDATE account_tax t
              SET name = jsonb_set(name, '{en_US}', to_jsonb('[old] ' || (name->>'en_US')))
             FROM bad_taxes
            WHERE t.id = bad_taxes.id
        RETURNING t.id
             )

      DELETE FROM ir_model_data d
       USING renamed_taxes t
       WHERE d.model = 'account.tax'
         AND d.res_id = t.id
        """
    )
