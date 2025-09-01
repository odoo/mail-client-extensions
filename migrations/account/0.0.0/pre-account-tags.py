# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~16.2"):
        return
    # `account.account` tags
    cr.execute(
        """
              SELECT at.account_account_tag_id, company.id, ARRAY_AGG(account.code)
                FROM account_account_template_account_tag at
                JOIN account_account_template account ON at.account_account_template_id = account.id
                JOIN res_company company ON company.chart_template_id = account.chart_template_id
            GROUP BY at.account_account_tag_id, company.id
            ORDER BY at.account_account_tag_id
        """
    )
    util.ENVIRON["account_tags_pre_config"] = cr.fetchall()

    # `account.tax` tags
    if all(
        util.table_exists(cr, table)
        for table in ["account_tax_account_tag", "account_account_tag_account_tax_template_rel"]
    ):
        cr.execute("SELECT COUNT(*) FROM account_tax_account_tag")
        if not cr.fetchone()[0]:
            # There is no tags configured on any taxes
            # This is mostly possible when the database was upgraded from 8.0 to 9.0 in the past and
            # the tags were not upgraded
            # We will try to configure the tags according to the tax templates.
            # We don't take much risks, since there is currently no configuration at all for tax tags anyway.
            # The matching is done on the name, description and type of use,
            # as it's done in
            # https://github.com/odoo/odoo/blob/80563819ae93c00d171935f1d1cded33de15ba21/addons/account/models/chart_template.py#L26
            # I would have liked to match the chart template of the tax company with the chart template of the tax template
            # But it seems it was fucked up during the upgrade from 8.0 to 9.0:
            # https://github.com/odoo/upgrade/blob/master/migrations/account/9.0.1.1/pre-25-chart-template.py#L14-L16
            # ```
            # SELECT tt.name, tt.chart_template_id, ct.name
            #   FROM account_tax_template tt
            #   JOIN account_chart_template ct ON ct.id = tt.chart_template_id
            #  WHERE tt.name = 'TVA collectée (vente) 20,0%'
            #             name             | chart_template_id |              name
            # -----------------------------+-------------------+---------------------------------
            # TVA collectée (vente) 20,0% |                 1 | Plan Comptable Général (France)
            #
            # SELECT t.name, c.id, c.chart_template_id, ct.name
            #   FROM account_tax t
            #   JOIN res_company c ON c.id = t.company_id JOIN account_chart_template ct ON ct.id = c.chart_template_id
            #  WHERE t.name = 'TVA collectée (vente) 20,0%'
            #             name             | id | chart_template_id |          name
            # -----------------------------+----+-------------------+-------------------------
            # TVA collectée (vente) 20,0% |  1 |                 3 | migration_chart_9_0_1_1
            # ```
            # I also considered the possibility to match on the XML Ids of the tax against the XML ids of the tax templates,
            # but XML ids are generated for taxes only from 10.0. In 9.0 or 8.0, no XML Ids where created when creating
            # tax from tax templates
            cr.execute(
                """
                WITH tags_set (tax_id, tag_id) AS
                (
                INSERT INTO account_tax_account_tag
                     SELECT tax.id, template_tags.account_account_tag_id
                       FROM account_tax tax
                  LEFT JOIN LATERAL
                            (
                                  SELECT *
                                    FROM account_tax_template template
                                   WHERE template.name = tax.name
                                     AND template.description = tax.description
                                     AND template.type_tax_use = tax.type_tax_use
                                ORDER BY id DESC LIMIT 1
                            ) template ON true
                  JOIN account_account_tag_account_tax_template_rel template_tags
                         ON template_tags.account_tax_template_id = template.id
                      WHERE template.id IS NOT NULL
                ON CONFLICT DO NOTHING
                  RETURNING account_tax_id, account_account_tag_id
                )
                SELECT tax.name, tag.name
                  FROM tags_set
                  JOIN account_tax tax ON tax.id = tags_set.tax_id
                  JOIN account_account_tag tag ON tag.id = tags_set.tag_id
                """
            )
            tax_tags = cr.fetchall()
            if tax_tags:
                li = "\n".join(
                    "<li>The tag {} has been added to the tax {}</li>".format(
                        util.html_escape(tag), util.html_escape(tax)
                    )
                    for tax, tag in tax_tags
                )
                util.add_to_migration_reports(
                    """
                        <details>
                        <summary>
                            Tags have been automatically set on taxes.
                            You must double-check the tags have been correctly mapped on your taxes.
                            If you want more tags to be automatically assigned on your taxes,
                            you must ensure the name, description and type of use of your taxes
                            match the ones of the tax templates.
                        </summary>
                        <ul>{}</ul>
                        </details>
                    """.format(li),
                    "Accounting",
                    format="html",
                )
