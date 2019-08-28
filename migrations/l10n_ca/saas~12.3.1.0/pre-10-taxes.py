# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        INSERT INTO taxes_not_to_merge(tax_id)
        SELECT res_id
        FROM ir_model_data
        WHERE
        (name LIKE '%gstpst\_bc\_sale\_en'
            OR name LIKE '%gstpst\_mb\_sale\_en'
            OR name LIKE '%gstqst\_sale\_en'
            OR name LIKE '%gstpst\_sk\_sale\_en'
            OR name LIKE '%gstpst\_bc\_purc\_en'
            OR name LIKE '%gstpst\_mb\_purc\_en'
            OR name LIKE '%gstqst\_purc\_en'
            OR name LIKE '%gstpst\_sk\_purc\_en')
        AND model = 'account.tax'
        AND module = 'l10n_ca'
    """)