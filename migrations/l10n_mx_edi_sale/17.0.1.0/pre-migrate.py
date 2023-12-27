# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "l10n_mx_edi_payment_method_id", "int4")
    default_pm = util.ref(cr, "l10n_mx_edi.payment_method_otros")

    query = cr.mogrify(
        """
        WITH so AS (
            SELECT o.id, p.l10n_mx_edi_payment_method_id
              FROM sale_order o
              JOIN res_company c
                ON c.id = o.company_id
              JOIN res_country n
                ON n.id = c.account_fiscal_country_id
         LEFT JOIN res_partner p
                ON p.id = o.partner_id
             WHERE n.code = 'MX'
               AND o.l10n_mx_edi_payment_method_id IS NULL
               AND {parallel_filter}
        )
        UPDATE sale_order o
           SET l10n_mx_edi_payment_method_id = COALESCE(so.l10n_mx_edi_payment_method_id, %s)
          FROM so
         WHERE so.id = o.id
        """,
        [default_pm],
    ).decode()

    util.explode_execute(cr, query, table="sale_order", alias="o")
