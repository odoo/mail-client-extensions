from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        SELECT id
          FROM ir_model_fields
         WHERE model='res.partner'
           AND name='property_payment_method_id'
    """)

    if cr.rowcount:
        old_field_id = cr.fetchone()[0]
        query = """
            SELECT id
              FROM ir_model_fields
             WHERE model = 'res.partner'
               AND name = 'property_outbound_payment_method_line_id'
         """
        cr.execute(query)
        new_field_id = cr.fetchone()[0]

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
            UPDATE ir_property p
               SET name = 'property_outbound_payment_method_line_id',
                   value_reference = CONCAT('payment.method.line,', pl.payment_method_line_id),
                   fields_id = %s
               FROM pay_lines pl
             WHERE p.fields_id = %s
               AND p.value_reference = CONCAT('payment.method,', pl.payment_method_id)
               AND p.company_id = pl.company_id
        """
        util.explode_execute(
            cr, cr.mogrify(query, [new_field_id, old_field_id]).decode(), table="ir_property", alias="p"
        )

    util.if_unchanged(cr, "account.journal_group_comp_rule", util.update_record_from_xml)
