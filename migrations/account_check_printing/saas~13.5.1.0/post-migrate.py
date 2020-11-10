# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("SELECT id from ir_model_fields WHERE model='res.partner' AND name='property_payment_method_id'")
    field_id = cr.fetchone()[0]
    cr.execute(
        """
        UPDATE account_move original
           SET preferred_payment_method_id=COALESCE(p1.value_integer,p2.value_integer)
          FROM account_move m
     LEFT JOIN ir_property p1 ON 'res.partner,'||m.partner_id=p1.res_id AND p1.fields_id=%s AND p1.company_id=m.company_id
     LEFT JOIN ir_property p2 ON 'res.partner,'||m.partner_id=p2.res_id AND p2.fields_id=%s AND p2.company_id IS NULL
         WHERE original.id=m.id
           AND original.preferred_payment_method_id IS NULL
    """,
        [field_id, field_id],
    )
