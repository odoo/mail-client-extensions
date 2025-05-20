from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import IntegrityCase, change_version


@change_version("saas~18.4")
class TestHrLeaveAllocationUnChanged(IntegrityCase):
    def invariant(self):
        self.skip_if_demo()
        cr = self.env.cr
        query = util.format_query(
            cr,
            """
                SELECT employee_id,
                       SUM(number_of_days)
                  FROM hr_leave_allocation
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
            expected_employee_id, expected_number_of_days = data_iter
            employee_id, number_of_days = new_data_iter
            self.assertEqual(expected_employee_id, employee_id)
            self.assertEqual(expected_number_of_days, number_of_days)
