from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id, fiscal_voluntary_rate FROM hr_employee WHERE fiscal_voluntary_rate > 0")
    rates = dict(cr.fetchall())
    for employee in util.iter_browse(util.env(cr)["hr.employee"], list(rates)):
        employee.message_post(body=f"Fiscal Voluntary Rate value was {rates.get(employee.id)}%", message_type="comment")
    if rates:
        util.add_to_migration_reports(
            "The field 'Fiscal Voluntary Rate' for employees is changed from a percentage "
            "to an amount. The value is not automatically converted, but the old rate is "
            "logged for each employee in the chatter.",
            "Belgium Payroll",
        )
    util.remove_field(cr, "hr.employee", "fiscal_voluntary_rate")
