# -*- coding: utf-8 -*-


def migrate(cr, version):
    mapping_table = [
        ('property_account_payable', 'property_account_payable_id'),
        ('property_account_receivable', 'property_account_receivable_id'),
        ('property_account_position', 'property_account_position_id'),
        ('property_payment_term', 'property_payment_term_id'),
        ('property_supplier_payment_term', 'property_supplier_payment_term_id'),
    ]
    for entry in mapping_table:
        cr.execute("""UPDATE ir_property
            SET name = %s, fields_id = field.id
            FROM (SELECT id FROM ir_model_fields WHERE name = %s and model = 'res.partner') field
            WHERE name = %s
            """, (entry[1], entry[1], entry[0]))
