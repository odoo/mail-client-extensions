from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase, change_version


@change_version("saas~18.4")
class TestHrLeaveUnChanged(IntegrityCase):
    def invariant(self):
        self.skip_if_demo()
        cr = self.env.cr
        query = util.format_query(
            cr,
            """
                SELECT employee_id,
                       SUM(number_of_days),
                       SUM(number_of_hours)
                  FROM hr_leave
                 WHERE state IN ('confirm', 'validate1', 'validate')
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
            expected_employee_id, expected_number_of_days, expected_number_of_hours = data_iter
            employee_id, number_of_days, number_of_hours = new_data_iter
            self.assertEqual(expected_employee_id, employee_id)
            self.assertEqual(expected_number_of_days, number_of_days)
            self.assertEqual(expected_number_of_hours, number_of_hours)
