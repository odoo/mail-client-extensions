from odoo.upgrade import util


def migrate(cr, version):
    # if column doesn't exist, it means there was no row in ir_property
    # for the property_payment_method_id. And the pre-migrate.py for
    # base didn't create a column for it
    if util.column_exists(cr, "res_partner", "property_payment_method_id"):
        # use '{{}}'::jsonb instead of '{}'::jsonb because the query str
        # will be format once in explode_execute
        query = """
            WITH pay_lines AS (
                SELECT l.payment_method_id,
                       j.company_id,
                       min(l.id) AS payment_method_line_id
                  FROM account_payment_method_line l
                  JOIN account_journal j
                    ON j.id = l.journal_id
              GROUP BY l.payment_method_id, j.company_id
            )
            UPDATE res_partner p
               SET property_outbound_payment_method_line_id =
                    NULLIF(
                        COALESCE(p.property_outbound_payment_method_line_id, '{{}}'::jsonb)
                     || COALESCE(
                            (SELECT jsonb_object_agg(key, pl.payment_method_line_id)
                               FROM pay_lines pl,
                                    jsonb_each(p.property_payment_method_id)
                              WHERE key = pl.company_id::text
                                AND value::int4 = pl.payment_method_id
                            ),
                            '{{}}'::jsonb
                        ),
                        '{{}}'::jsonb
                    )
             WHERE p.property_payment_method_id IS NOT NULL
        """
        util.explode_execute(cr, query, table="res_partner", alias="p")

    util.if_unchanged(cr, "account.journal_group_comp_rule", util.update_record_from_xml)
