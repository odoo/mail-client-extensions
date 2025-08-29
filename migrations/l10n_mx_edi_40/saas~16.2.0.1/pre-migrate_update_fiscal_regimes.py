from odoo.upgrade import util


def migrate(cr, version):
    if util.parse_version(version) >= util.parse_version("saas~16.2"):
        # may be called by `l10n_mx_edi/saas~16.3`, but should only be run for pre-16.2 databases
        return  # nosemgrep: no-early-return
    # in case the script is called by 'l10n_mx_edi/saas~16.3' and l10n_mx_edi_40 was not previously installed
    if util.create_column(cr, "res_partner", "l10n_mx_edi_fiscal_regime", "varchar"):
        populate_column_query = """
            UPDATE res_partner
               SET l10n_mx_edi_fiscal_regime = CASE res_country.code
                                               WHEN 'MX' THEN '616'
                                               ELSE '601'
                   END
              FROM res_country
             WHERE res_country.id = res_partner.country_id
        """
        util.explode_execute(cr, populate_column_query, table="res_partner")
    else:
        query_no_country = """
            UPDATE res_partner
               SET l10n_mx_edi_fiscal_regime = NULL
             WHERE country_id IS NULL
        """
        query_foreign_partners = """
            UPDATE res_partner
               SET l10n_mx_edi_fiscal_regime = '616'
              FROM res_country
             WHERE res_country.id = res_partner.country_id
               AND res_country.code != 'MX'
               AND l10n_mx_edi_fiscal_regime IS DISTINCT FROM '616'
        """
        util.explode_execute(cr, query_no_country, table="res_partner")
        util.explode_execute(cr, query_foreign_partners, table="res_partner")
