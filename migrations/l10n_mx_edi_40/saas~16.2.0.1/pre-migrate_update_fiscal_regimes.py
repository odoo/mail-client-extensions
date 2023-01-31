from odoo.upgrade import util


def migrate(cr, version):
    query_no_country = """
        UPDATE res_partner
           SET l10n_mx_edi_fiscal_regime = NULL
         WHERE country_id IS NULL
    """

    query_foreign_partners = """
        UPDATE res_partner
           SET l10n_mx_edi_fiscal_regime = 616
          FROM res_country
         WHERE res_country.id = res_partner.country_id
           AND res_country.code != 'MX'
    """

    util.parallel_execute(cr, util.explode_query_range(cr, query_no_country, table="res_partner"))
    util.parallel_execute(cr, util.explode_query_range(cr, query_foreign_partners, table="res_partner"))
