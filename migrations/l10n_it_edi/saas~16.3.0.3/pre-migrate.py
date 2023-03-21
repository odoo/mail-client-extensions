# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE account_edi_proxy_client_user u
           SET proxy_type = 'l10n_it_edi'
          FROM res_company c
          JOIN res_country t
            ON t.id = c.country_id
         WHERE c.id = u.company_id
           AND t.code = 'IT'
    """

    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_edi_proxy_client_user"))
