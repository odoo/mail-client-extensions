from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_es_is_simplified", "bool", default=False)
    simplified_partner = util.ref(cr, "l10n_es_edi_sii.partner_simplified")
    eb = util.expand_braces

    if simplified_partner:
        util.rename_xmlid(cr, *eb("{l10n_es_edi_sii,l10n_es}.partner_simplified"))
        query = cr.mogrify(
            """
               UPDATE account_move m
                  SET l10n_es_is_simplified='t'
                WHERE m.partner_id=%s
            """,
            (simplified_partner,),
        ).decode()
        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                query,
                table="account_move",
                alias="m",
            ),
        )

    util.move_field_to_module(cr, "account.tax", "l10n_es_type", "l10n_es_edi_sii", "l10n_es")
    util.move_field_to_module(cr, "account.tax", "l10n_es_exempt_reason", "l10n_es_edi_sii", "l10n_es")
    util.move_field_to_module(cr, "account.tax", "l10n_es_bien_inversion", "l10n_es_edi_sii", "l10n_es")

    util.rename_xmlid(cr, *eb("{l10n_es_edi_sii,l10n_es}.account_tax_form_inherit_l10n_es_edi"))
