from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    for company in env["res.company"].search([("chart_template", "!=", False)]):
        ChartTemplate = env["account.chart.template"].with_company(company)
        data = ChartTemplate._get_chart_template_data(company.chart_template).get("template_data")
        if data and data.get("downpayment_account_id"):
            property_downpayment_account = (
                env["account.chart.template"]
                .with_company(company)
                .ref(data["downpayment_account_id"], raise_if_not_found=False)
            )
            if property_downpayment_account:
                company.downpayment_account_id = property_downpayment_account
