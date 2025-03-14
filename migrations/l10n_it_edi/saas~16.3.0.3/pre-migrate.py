from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE account_edi_proxy_client_user u
           SET proxy_type = 'l10n_it_edi'
          FROM res_company c
          JOIN res_partner p
            ON p.id = c.partner_id
          JOIN res_country t
            ON t.id = p.country_id
         WHERE c.id = u.company_id
           AND t.code = 'IT'
    """

    util.explode_execute(cr, query, table="account_edi_proxy_client_user", alias="u")
