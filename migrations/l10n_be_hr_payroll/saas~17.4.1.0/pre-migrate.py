from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "fiscal_voluntary_rate", "float8")
    cr.execute("""
    UPDATE hr_employee e
       SET fiscal_voluntary_rate = c.fiscal_voluntary_rate
      FROM hr_contract c
     WHERE c.id = e.contract_id
       AND c.fiscal_voluntarism = true
    """)

    util.remove_field(cr, "hr.contract", "fiscal_voluntarism")
    util.remove_field(cr, "hr.contract", "fiscal_voluntary_rate")

    util.remove_field(cr, "hr.contract.history", "fiscal_voluntarism")
    util.remove_field(cr, "hr.contract.history", "fiscal_voluntary_rate")

    util.remove_field(cr, "l10n.be.double.pay.recovery.wizard", "classic_holiday_pay")
