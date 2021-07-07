# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    """
    Sets property_tax_payable_account_id and property_tax_receivable_account_id
    to account "260500 erario c/IVA".
    """

    cr.execute(
        """
            INSERT INTO ir_property (name, fields_id, company_id, type, value_reference)
                 SELECT imf.name,
                        imf.id,
                        com.id,
                        'many2one',
                        'account.account,' || %s
                   FROM res_company com
                   JOIN res_country cou ON cou.id = com.account_fiscal_country_id
             CROSS JOIN ir_model_fields imf
                  WHERE cou.code = 'IT'
                    AND imf.model = 'account.tax.group'
                    AND imf.name in ('property_tax_payable_account_id',
                                     'property_tax_receivable_account_id')
            ON CONFLICT DO NOTHING
        """,
        (str(util.ref(cr, "l10n_it.2605")),),
    )
