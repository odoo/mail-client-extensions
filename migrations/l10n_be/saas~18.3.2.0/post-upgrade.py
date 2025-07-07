from odoo.upgrade import util

NEW_TAXES = [
    "attn_VAT-IN-V83-277-ROW-CC",
    "attn_VAT-IN-V82-S-ND",
    "attn_VAT-IN-V83-IG-ND",
]
NEW_ACCOUNTS = [
    "a241",
    "a2411",
    "a6102",
    "a61021",
    "a610211",
    "a610212",
    "a610213",
    "a61022",
    "a61031",
    "a611201",
    "a612901",
    "a61291",
    "a613311",
    "a6144",
    "a616506",
    "a61651",
    "a61654",
    "a616541",
    "a6234",
    "a623401",
    "a62361",
    "a6402",
    "a645",
]


def migrate(cr, version):
    # Due to the change of the `auto_install` flags, the module `l10n_be_disallowed_expenses` will be installed.
    # During the install, it will try to update the `account.account` of the Belgian CoA, including new accounts. Force creation of
    # those new accounts.
    env = util.env(cr)
    domain = [("chart_template", "in", ["be", "be_comp", "be_asso"]), ("parent_id", "=", False)]
    for company in env["res.company"].search(domain, order="id"):
        ChartTemplate = env["account.chart.template"].with_company(company)
        taxes = {k: v for k, v in ChartTemplate._get_account_tax(company.chart_template).items() if k in NEW_TAXES}
        accounts = {
            k: v for k, v in ChartTemplate._get_account_account(company.chart_template).items() if k in NEW_ACCOUNTS
        }
        ChartTemplate._load_data({"account.tax": taxes, "account.account": accounts})
