from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_payroll_account.hr_salaries_account_journal", True)
    util.ensure_xmlid_match_record(
        cr,
        "hr_payroll_account.hr_payroll_account_journal",
        "account.journal",
        {
            "code": "SLR",
            "company_id": util.env(cr).user.company_id.id,
        },
    )
