from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    for company in env["res.company"].search([("chart_template", "!=", False)], order="parent_path"):
        ChartTemplate = env["account.chart.template"].with_company(company)
        ChartTemplate._load_data(
            {
                "account.reconcile.model": ChartTemplate._get_account_reconcile_model(company.chart_template),
            },
            ignore_duplicates=True,
        )
