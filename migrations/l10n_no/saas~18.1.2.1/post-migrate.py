from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    norway_companies = env["res.company"].search([("chart_template", "=", "no")])
    if norway_companies:
        norway_template_data_taxes = env["account.chart.template"]._get_chart_template_data("no")["account.tax"]
        tax_xmlid_to_standard_code = {
            f"{company.id}_{tax_xmlid}": tax_data.get("l10n_no_standard_code")
            for company in norway_companies
            for tax_xmlid, tax_data in norway_template_data_taxes.items()
        }

        if tax_xmlid_to_standard_code:
            cr.execute(
                """
                UPDATE account_tax tax
                   SET l10n_no_standard_code = txtsc.standard_code
                  FROM json_each_text(%s) as txtsc(xmlid, standard_code)
                  JOIN ir_model_data imd
                    ON imd.module = 'account'
                   AND imd.name = txtsc.xmlid
                 WHERE tax.id = imd.res_id
                """,
                [util.json.dumps(tax_xmlid_to_standard_code)],
            )
