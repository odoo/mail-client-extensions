# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE sale_order o
           SET l10n_mx_edi_cfdi_to_public = true
          FROM res_company c
          JOIN res_partner p
            ON p.id = c.partner_id
          JOIN res_country y
            ON y.id = p.country_id
         WHERE c.id = o.company_id
           AND y.code = 'MX'
           AND o.website_id IS NOT NULL
    """
    util.explode_execute(cr, query, table="sale_order", alias="o")
