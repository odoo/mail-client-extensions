from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("15.0")
class PR3445(UpgradeCase):
    def prepare(self):
        emp = self.env["hr.employee"].create({"name": "Georges Abitbol"})
        payslip = self.env["hr.payslip"].create(
            {
                "name": "Apr 2022",
                "employee_id": emp.id,
                "date_from": datetime.strptime("2022-04-01", "%Y-%m-%d"),
                "date_to": datetime.strptime("2022-04-30", "%Y-%m-%d"),
            }
        )
        payslip._onchange_employee()
        return payslip.id

    def check(self, data):
        self.assertTrue(data)
