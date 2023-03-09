from odoo.tools.translate import _

from odoo.upgrade import util


def migrate(cr, version):
    account = util.env(cr)["account.account"]

    for company in util.env(cr)["res.company"].search([]):
        account = self = account.with_context(  # noqa F841
            lang=company.partner_id.lang, _upg_ignore_earning_accounts_check=True
        ).with_company(company)
        account_type_current_assets = util.ref(cr, "account.data_account_type_current_assets")
        chart_template = company.chart_template_id
        if not chart_template:
            continue
        # account_journal_payment_credit_account_id and account_journal_payment_debit_account_id
        # are new fields in 14.3, set them with newly created bank accounts
        company.account_journal_payment_credit_account_id = account.create(
            {
                "name": _("Outstanding Payments"),
                "code": account._search_new_account_code(
                    company, chart_template.code_digits, company.bank_account_code_prefix or ""
                ),
                "reconcile": True,
                "user_type_id": account_type_current_assets,
                "company_id": company.id,
            }
        )
        company.account_journal_payment_debit_account_id = account.create(
            {
                "name": _("Outstanding Receipts"),
                "code": account._search_new_account_code(
                    company, chart_template.code_digits, company.bank_account_code_prefix or ""
                ),
                "reconcile": True,
                "user_type_id": account_type_current_assets,
                "company_id": company.id,
            }
        )
