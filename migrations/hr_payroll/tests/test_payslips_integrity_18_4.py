from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase, change_version


@change_version("saas~18.4")
class TestHrPaySlipUnChanged(IntegrityCase):
    def prepare(self):
        if not util.version_gte("18.0"):
            return None
        return super().prepare()

    def invariant(self):
        self.skip_if_demo()
        cr = self.env.cr
        query = util.format_query(
            cr,
            """
                SELECT p.employee_id,
                       SUM(p.basic_wage),
                       SUM(p.gross_wage),
                       SUM(p.net_wage)
                  FROM hr_payslip p
                 WHERE p.state IN ('done', 'paid')
              GROUP BY employee_id
              ORDER BY employee_id
            """,
        )
        cr.execute(query)
        return cr.fetchall()

    def check(self, value):
        if not value:
            return
        new_data = self.invariant()
        for data_iter, new_data_iter in zip(value, new_data):
            expected_employee_id, expected_basic_wage, expected_gross_wage, expected_net_wage = data_iter
            employee_id, basic_wage, gross_wage, net_wage = new_data_iter
            self.assertEqual(expected_employee_id, employee_id)
            self.assertEqual(expected_basic_wage, basic_wage)
            self.assertEqual(expected_gross_wage, gross_wage)
            self.assertEqual(expected_net_wage, net_wage)
