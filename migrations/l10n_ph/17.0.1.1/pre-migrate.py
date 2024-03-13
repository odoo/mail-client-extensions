from odoo.upgrade import util


def migrate(cr, version):
    ph = util.ref(cr, "base.ph")
    us = util.ref(cr, "base.us")

    cr.execute(
        """
        UPDATE res_company
           SET account_fiscal_country_id = %s
         WHERE chart_template = 'ph'
           AND account_fiscal_country_id = %s
     RETURNING id, name
        """,
        [ph, us],
    )
    companies = cr.fetchall()

    cr.execute(
        r"""
         UPDATE account_tax_group AS atg
            SET country_id = %s
           FROM ir_model_data AS imd,
                res_company AS rc
          WHERE atg.country_id = %s
            AND atg.company_id = rc.id
            AND rc.chart_template = 'ph'
            AND imd.module = 'account'
            AND imd.model = 'account.tax.group'
            AND imd.name ~ '^\d+_l10n_ph_.+'
            AND imd.res_id = atg.id
      RETURNING atg.id, atg.name->'en_US'
        """,
        [ph, us],
    )
    tax_groups = cr.fetchall()

    cr.execute(
        """
        UPDATE account_tax
           SET country_id = %s
         WHERE tax_group_id = ANY(%s)
           AND country_id = %s
     RETURNING id, name->'en_US'
        """,
        [ph, [tg[0] for tg in tax_groups], us],
    )
    taxes = cr.fetchall()

    if companies or tax_groups:
        util.add_to_migration_reports(
            f"""
                <details>
                    <summary>
                        Some companies or taxes had their fiscal country set to United States instead of Philippines.
                        The following records have been updated and have now their fiscal country set to Philippines.
                    </summary>
                    <h4>Companies</h4>
                    <ul>{"".join(f"<li>{util.get_anchor_link_to_record('res.company', id, name)}</li>"
                                for id, name in companies)}</ul>
                    <h4>Tax groups</h4>
                    <ul>{"".join(f"<li>{util.get_anchor_link_to_record('account.tax.group', id, name)}</li>"
                                for id, name in tax_groups)}</ul>
                    <h4>Taxes</h4>
                    <ul>{"".join(f"<li>{util.get_anchor_link_to_record('account.tax', id, name)}</li>"
                                for id, name in taxes)}</ul>
                </details>
            """,
            category="Philippines - Accounting",
            format="html",
        )
