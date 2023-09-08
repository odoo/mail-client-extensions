from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment"):
        util.move_field_to_module(cr, "hr.employee", "newly_hired_employee", "hr_recruitment", "hr")
        util.rename_field(cr, "hr.employee", "newly_hired_employee", "newly_hired")

    util.create_column(cr, "hr_contract_type", "code", "varchar")

    util.explode_execute(
        cr,
        "UPDATE hr_contract_type SET code = name->>'en_US'",
        table="hr_contract_type",
    )

    util.move_field_to_module(cr, "hr.departure.reason", "reason_code", "l10n_be_hr_payroll", "hr")
