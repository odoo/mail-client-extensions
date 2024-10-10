from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_fr.res_partner_form_l10n_fr")

    util.explode_execute(
        cr,
        """
        UPDATE res_partner
           SET company_registry = siret
         WHERE siret IS NOT NULL
           AND company_registry IS NULL
           AND {parallel_filter}
     RETURNING id
        """,
        table="res_partner",
    )
    overwritten_company_reg_count = util.explode_execute(
        cr,
        """
        UPDATE res_partner
           SET company_registry = siret,
               comment = CONCAT(
                           'Previous company registry: ', company_registry, '\n',
                            COALESCE(comment, '')
                         )
         WHERE siret != company_registry
           AND {parallel_filter}
     RETURNING id
        """,
        table="res_partner",
    )

    if overwritten_company_reg_count:
        util.add_to_migration_reports(
            category="Accounting",
            message=f"""
            The field Siret will be removed, Company Registry should be used instead.
            {overwritten_company_reg_count} partner(s) had both Company Registry and Siret defined, with different values.
            The old value of Company Registry was kept as an internal note in the partners for which a Siret was also set.
            If you find any issue, please review the data before the upgrade and
            remove or update one of the values on the partners before requesting another upgrade.
            """,
        )

    util.remove_field(cr, "res.company", "siret")
    util.remove_field(cr, "res.partner", "siret")
