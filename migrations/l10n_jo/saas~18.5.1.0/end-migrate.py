from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    for company in env["res.company"].search([("chart_template", "=", "jo_standard")], order="parent_path"):
        env["account.chart.template"].try_loading("jo_standard", company)

    tax_xmlid_regex = (
        "(?:"
        + "|".join(
            (
                r"^\d+_jo_zero_sale_0$",
                r"^\d+_jo_zero_sale_export$",
                r"^\d+_jo_zero_sale_no_tax$",
                r"^\d+_jo_zero_sale_exempted$",
                r"^\d+_jo_standard_purchase_import_deferred$",
                r"^\d+_eg_zero_purchase_exempted$",
            )
        )
        + ")"
    )

    # Delete the tax tags from repartition lines that has type tax and matches the above xmlids.
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel AS tag_rel
              USING account_tax_repartition_line rep_line
               JOIN account_tax as tax
                 ON tax.id = rep_line.tax_id
               JOIN res_country as country
                 ON country.id = tax.country_id
                AND country.code = 'JO'
               JOIN ir_model_data imd_taxes
                 ON imd_taxes.res_id = tax.id
                AND imd_taxes.model = 'account.tax'
              WHERE rep_line.id = tag_rel.account_tax_repartition_line_id
                AND rep_line.repartition_type = 'tax'
                AND imd_taxes.name ~ %s
                AND imd_taxes.module = 'account'
        """,
        [tax_xmlid_regex],
    )

    # Remove the account of the repartition lines that has type tax and matches the above xmlids.
    cr.execute(
        """
        UPDATE account_tax_repartition_line rep_line
           SET account_id = NULL
          FROM account_tax tax
          JOIN res_country as country
            ON country.id = tax.country_id
           AND country.code = 'JO'
          JOIN ir_model_data imd_taxes
            ON imd_taxes.res_id = tax.id
           AND imd_taxes.model = 'account.tax'
         WHERE tax.id = rep_line.tax_id
           AND rep_line.repartition_type = 'tax'
           AND rep_line.account_id IS NOT NULL
           AND imd_taxes.name ~ %s
           AND imd_taxes.module = 'account'
        """,
        [tax_xmlid_regex],
    )
