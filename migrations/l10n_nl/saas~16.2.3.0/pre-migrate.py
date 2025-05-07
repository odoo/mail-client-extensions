from odoo.upgrade import util


def migrate(cr, version):
    """
    Try to infer the value of the fields peppol_endpoint and peppol_eas.
    Copy the value of:
    * l10n_nl_oin on the field peppol_endpoint and set peppol_eas to '0190' if it's set
    * l10n_nl_kvk on the field peppol_endpoint and set peppol_eas to '0106' if it's set
    * vat on the field peppol_endpoint and set peppol_eas to '9944' if it's set
    """
    query = """
        UPDATE res_partner p
           SET peppol_endpoint = COALESCE(l10n_nl_kvk, l10n_nl_oin, vat),
               peppol_eas = (
               CASE
                    WHEN l10n_nl_kvk IS NOT NULL THEN '0106'
                    WHEN l10n_nl_oin IS NOT NULL THEN '0190'
                    WHEN vat IS NOT NULL THEN '9944'
               END)
          FROM res_country c
         WHERE c.id = p.country_id AND c.code = 'NL'
    """
    if util.column_exists(cr, "res_partner", "peppol_endpoint"):
        util.explode_execute(cr, query, table="res_partner", alias="p")

    util.remove_field(cr, "res.partner", "l10n_nl_kvk")
    util.remove_field(cr, "res.company", "l10n_nl_kvk")
    util.remove_field(cr, "res.partner", "l10n_nl_oin")
    util.remove_field(cr, "res.company", "l10n_nl_oin")
    util.remove_view(cr, "l10n_nl.view_partner_form_inherit_l10n_nl")
    util.remove_view(cr, "l10n_nl.res_company_form_inherit_nl")
