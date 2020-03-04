# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO ir_property(name, fields_id, company_id, res_id, type, value_text)
             SELECT 'property_ups_carrier_account',
                    (SELECT id FROM ir_model_fields WHERE model = 'res.partner' AND name = 'property_ups_carrier_account'),
                    company_id,
                    partner_id,
                    'char',
                    (array_agg(partner_ups_carrier_account ORDER BY state in ('done', 'sent') desc, date_order desc))[1]

              FROM sale_order
             WHERE partner_ups_carrier_account IS NOT NULL
          GROUP BY partner_id, company_id
       ON CONFLICT DO NOTHING
    """
    )

    util.remove_column(cr, "sale_order", "partner_ups_carrier_account")
