# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "l10n.in.report.account")
    util.create_column(cr, "account_move", "l10n_in_transaction_type", "character varying")
    query = """
        UPDATE account_move m
           SET l10n_in_transaction_type = CASE
                   WHEN m.l10n_in_state_id = partner.state_id THEN 'intra_state'
                   ELSE 'inter_state'
               END
          FROM res_company company
          JOIN res_country country
            ON company.account_fiscal_country_id = country.id
          JOIN res_partner partner
            ON partner.id = company.partner_id
         WHERE m.company_id = company.id
           AND country.code = 'IN'
    """
    util.explode_execute(cr, query, table="account_move", alias="m")
