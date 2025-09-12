from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    query = """
        SELECT id
          FROM hr_expense
         WHERE company_currency_id IS NOT NULL
           AND total_amount_company IS NULL
    """
    util.recompute_fields(cr, "hr.expense", ["total_amount_company"], query=query)
