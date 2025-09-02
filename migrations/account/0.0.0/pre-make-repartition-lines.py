from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Starting saas~16.3 the missing repartition lines are recreated by the ORM
    if util.version_between("15.0", "saas~16.2"):
        _create_repartition_lines(cr)


def _create_repartition_lines(cr):
    # invoice_tax_id and refund_tax_id becomes tax_id in saas~16.2
    if util.column_exists(cr, "account_tax_repartition_line", "tax_id"):
        cr.execute(
            """
            WITH info AS (
                SELECT tax.type AS ttype,
                       doc.type AS dtype,
                       array_agg(rl.tax_id) AS tax_ids
                  FROM (VALUES ('tax'), ('base')) AS tax(type)
            CROSS JOIN (VALUES ('invoice'), ('refund')) AS doc(type)
             LEFT JOIN account_tax_repartition_line rl
                    ON rl.repartition_type = tax.type
                   AND rl.document_type = doc.type
                 WHERE rl.tax_id IS NOT NULL
             GROUP BY tax.type, doc.type
            )
            INSERT INTO account_tax_repartition_line(
                            repartition_type,document_type,factor_percent,tax_id,company_id,sequence
                        )
                 SELECT info.ttype, info.dtype, 100.0, t.id, t.company_id,
                   CASE WHEN info.ttype = 'base' THEN 1 ELSE 2 END AS sequence
                   FROM info,
                        account_tax t
                  WHERE t.amount_type != 'group'
                    AND t.id != ALL(info.tax_ids)
            """
        )
    else:
        cr.execute(
            """
            WITH info AS (
                SELECT tax.type AS ttype,
                       doc.type AS dtype,
                       array_agg(
                           CASE doc.type
                               WHEN 'invoice' THEN rl.invoice_tax_id
                               ELSE rl.refund_tax_id
                           END
                       ) AS tax_ids
                  FROM (VALUES ('tax'), ('base')) AS tax(type)
            CROSS JOIN (VALUES ('invoice'), ('refund')) AS doc(type)
             LEFT JOIN account_tax_repartition_line rl
                    ON rl.repartition_type = tax.type
                 WHERE (doc.type = 'invoice' AND rl.invoice_tax_id IS NOT NULL)
                    OR (doc.type = 'refund' AND rl.refund_tax_id IS NOT NULL)
              GROUP BY tax.type, doc.type
            )
            INSERT INTO account_tax_repartition_line(
                            repartition_type,invoice_tax_id,refund_tax_id,factor_percent,company_id,sequence
                        )
                 SELECT info.ttype,
                        CASE
                            WHEN info.dtype = 'invoice' THEN t.id
                            ELSE NULL
                        END AS invoice_tax_id,
                        CASE
                            WHEN info.dtype = 'refund' THEN t.id
                            ELSE NULL
                        END AS refund_tax_id,
                        100.0,
                        t.company_id,
                        CASE WHEN info.ttype = 'base' THEN 1 ELSE 2 END AS sequence
                   FROM info,
                        account_tax t
                  WHERE t.amount_type != 'group'
                    AND t.id != ALL(info.tax_ids)
            """
        )
