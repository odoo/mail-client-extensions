from odoo.addons.account_edi_ubl_cii.models.account_edi_common import EAS_MAPPING

from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "res_partner", "l10n_lu_peppol_identifier"):
        util.rename_field(cr, "res.partner", "l10n_lu_peppol_identifier", "peppol_endpoint")
    else:
        util.create_column(cr, "res_partner", "peppol_endpoint", "varchar")
    util.create_column(cr, "res_partner", "peppol_eas", "varchar")
    util.create_column(cr, "res_partner", "ubl_cii_format", "varchar")

    subquery_eas = "CASE "
    subquery_endpoint = "CASE WHEN p.peppol_endpoint IS NOT NULL THEN p.peppol_endpoint "

    for country_code, country_map in EAS_MAPPING.items():
        eas_code = next(iter(country_map))
        field = country_map[eas_code]
        if country_code != "NL":  # NL case is treated in l10n_nl
            # Mimick _compute_peppol_eas: get the first eas_code and set it
            subquery_eas += cr.mogrify("WHEN c.code = %s THEN %s ", [country_code, eas_code]).decode()
            # Mimick _compute_peppol_endpoint: get the corresponding field and set it
            if field and util.column_exists(cr, "res_partner", field):
                subquery_endpoint += cr.mogrify(
                    util.format_query(cr, "WHEN c.code = %s THEN p.{} ", field),
                    [country_code],
                ).decode()

    subquery_eas += "END"
    subquery_endpoint += "END"

    query = util.format_query(
        cr,
        """
        UPDATE res_partner p
           SET ubl_cii_format = (
               CASE
                    WHEN c.code = 'FR' THEN 'facturx'
                    WHEN c.code = 'DE' THEN 'xrechnung'
                    WHEN c.code = 'NL' THEN 'nlcius'
                    WHEN c.code in ('AU', 'NZ') THEN 'ubl_a_nz'
                    WHEN c.code = 'SG' THEN 'ubl_sg'
                    WHEN c.code IN %s THEN 'ubl_bis3'
               END),
               peppol_eas = {},
               peppol_endpoint = {}
          FROM res_country c
         WHERE c.id = p.country_id
           AND p.parent_id IS NULL
        """,
        util.SQLStr(subquery_eas),
        util.SQLStr(subquery_endpoint),
    )
    query = cr.mogrify(
        query,
        [tuple(set(EAS_MAPPING.keys()) - {"FR", "DE", "NL", "AU", "NZ", "SG"})],
    ).decode()
    util.explode_execute(cr, query, table="res_partner", alias="p")

    util.remove_field(cr, "res.partner", "l10n_lu_peppol_identifier")
    util.remove_view(cr, "account_edi_ubl_cii.res_partner_form_inherit_l10n_lu_peppol_id")
