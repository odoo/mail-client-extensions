from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO ir_property(name, fields_id, company_id, type, value_reference)
             SELECT 'journal_id',
                    (SELECT id FROM ir_model_fields WHERE model = 'hr.payroll.structure' AND name = 'journal_id'),
                    id,
                    'many2one',
                    %s
              FROM res_company
       ON CONFLICT DO NOTHING
    """,
        ["account.journal," + str(util.ref(cr, "hr_payroll_account.hr_payroll_account_journal"))],
    )
