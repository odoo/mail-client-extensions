from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.4")
class TestMigrateEmployeeWithContract(UpgradeCase):
    @property
    def key(self):
        return "hr_contract.tests.test_migrate_employee_with_contract_18_4.TestMigrateEmployeeWithContract"

    def _set_value(self, key, value):
        # Completely ignore the prepare from this class, only use the one from
        #  `hr_contract`
        return

    def prepare(self):
        return []

    def check(self, init):
        (
            employee_ids,
            contracts_count,
            resource_calendar_id,
            department_id,
            job_ids,
            structure_type_id,
            contract_type_ids,
        ) = init
        employees = (
            employee1,
            employee2,
            employee3,
            employee4,
            employee5,
            employee6,
            employee7,
            employee8,
        ) = self.env["hr.employee"].browse(employee_ids)
        developer_job, team_leader_job = self.env["hr.job"].browse(job_ids)
        contract_type_cdi, contract_type_cdd = self.env["hr.contract.type"].browse(contract_type_ids)
        contract_template = self.env["hr.version"].search(
            [("employee_id", "=", False), ("name", "=", "UPGRADE_saas18.4-contract_template")]
        )
        self.assertTrue(contract_template, "a contract template should be found")
        self.assertEqual(contract_template.date_version, date.today())
        self.assertEqual(contract_template.contract_date_start, date.today())
        self.assertEqual(contract_template.wage, 2000)
        self.assertEqual(contract_template.structure_type_id.id, structure_type_id)
        self.assertEqual(contract_template.department_id.id, department_id)
        self.assertEqual(contract_template.job_id, developer_job)
        self.assertEqual(contract_template.resource_calendar_id.id, resource_calendar_id)
        self.assertEqual(contract_template.trial_date_end, date.today() + relativedelta(months=1))
        self.assertEqual(contract_template.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(contract_template.contract_type_id, contract_type_cdd)
        self.assertEqual(contract_template.hr_responsible_id, self.env.user)

        self.assertTrue(employees.exists(), "All employees should still exist after migration")
        self.assertEqual(
            len(employees.with_context(active_test=False).version_ids + contract_template),
            contracts_count + 3,
            "The number of versions generated should be equal to the number of contracts created before migration + one version for the second employee since the draft contract will be archived he needs an active version",
        )
        self.assertTrue(employee1.version_id, "A version should exist for that employee")
        self.assertEqual(len(employee1.with_context(active_test=False).version_ids), 1)
        employee_version = employee1.version_id
        self.assertEqual(employee_version.date_version, date(2022, 10, 10))
        self.assertEqual(employee_version.contract_date_start, date(2022, 10, 10))
        self.assertEqual(employee_version.wage, 3000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, team_leader_job)
        self.assertEqual(employee_version.contract_type_id, contract_type_cdi)
        self.assertFalse(employee_version.resource_calendar_id)
        self.assertEqual(employee_version.trial_date_end, date(2023, 1, 10))
        self.assertFalse(employee_version.contract_date_end)
        self.assertEqual(employee_version.children, 1)
        self.assertEqual(employee_version.marital, "married")

        self.assertTrue(employee2.version_id, "A version should exist for that employee")
        self.assertEqual(len(employee2.with_context(active_test=False).version_ids), 2)
        employee_version = employee2.version_id
        self.assertEqual(employee_version.date_version, date.today())
        self.assertFalse(employee_version.contract_date_start)
        self.assertFalse(employee_version.wage)
        self.assertNotEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertFalse(employee_version.department_id)
        self.assertFalse(employee_version.job_id)
        self.assertEqual(employee_version.resource_calendar_id.id, resource_calendar_id)
        self.assertFalse(employee_version.trial_date_end)
        self.assertFalse(employee_version.contract_date_end)
        self.assertTrue(employee_version.active)

        employee_version = employee2.with_context(active_test=False).version_ids - employee_version
        self.assertFalse(employee_version.active, "The draft contract should be converted into an archived version.")
        self.assertEqual(employee_version.contract_date_start, date.today() + relativedelta(days=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertEqual(employee_version.contract_type_id, contract_type_cdd)
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        self.assertTrue(employee3.version_id, "A version should exist for that employee")
        self.assertEqual(len(employee3.with_context(active_test=False).version_ids), 2)
        employee_version = employee3.version_id
        self.assertEqual(employee_version.date_version, date.today())
        self.assertFalse(employee_version.contract_date_start)
        self.assertFalse(employee_version.wage)
        self.assertNotEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertFalse(employee_version.department_id)
        self.assertFalse(employee_version.job_id)
        self.assertEqual(employee_version.resource_calendar_id.id, resource_calendar_id)
        self.assertFalse(employee_version.trial_date_end)
        self.assertFalse(employee_version.contract_date_end)
        self.assertTrue(employee_version.active)

        employee_version = employee3.with_context(active_test=False).version_ids - employee_version
        self.assertTrue(
            employee_version.active, "The draft contract ready should be converted into future version of the employee."
        )
        self.assertEqual(employee_version.contract_date_start, date.today() + relativedelta(days=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertFalse(employee_version.contract_type_id)
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        self.assertTrue(employee4.version_id)
        self.assertEqual(len(employee4.with_context(active_test=False).version_ids), 2)
        employee_version = employee4.version_id
        self.assertEqual(employee_version.date_version, date.today())
        self.assertFalse(employee_version.contract_date_start)
        self.assertFalse(employee_version.wage)
        self.assertNotEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertFalse(employee_version.department_id)
        self.assertFalse(employee_version.job_id)
        self.assertEqual(employee_version.resource_calendar_id.id, resource_calendar_id)
        self.assertFalse(employee_version.trial_date_end)
        self.assertFalse(employee_version.contract_date_end)
        self.assertTrue(employee_version.active)

        employee_version = employee4.with_context(active_test=False).version_ids - employee_version
        self.assertTrue(employee_version.active, "The expired contract should be converted into version in the past.")
        self.assertEqual(employee_version.contract_date_start, date.today() - relativedelta(months=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertFalse(employee_version.contract_type_id)
        self.assertEqual(employee_version.contract_date_end, date.today() - relativedelta(days=1))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        self.assertTrue(employee5.version_id)
        self.assertEqual(len(employee5.with_context(active_test=False).version_ids), 2)
        employee_version = employee5.version_id
        self.assertEqual(employee_version.date_version, date(2022, 10, 10))
        self.assertEqual(employee_version.contract_date_start, date(2022, 10, 10))
        self.assertEqual(employee_version.wage, 3000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, team_leader_job)
        self.assertTrue(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertEqual(employee_version.trial_date_end, date(2023, 1, 10))
        self.assertFalse(employee_version.contract_date_end)

        employee_version = employee5.with_context(active_test=False).version_ids - employee_version
        self.assertFalse(employee_version.active, "The draft contract should be converted into an archived version.")
        self.assertEqual(employee_version.contract_date_start, date.today() + relativedelta(days=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertEqual(employee_version.contract_type_id, contract_type_cdd)
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        self.assertTrue(employee6.version_id)
        self.assertEqual(len(employee6.with_context(active_test=False).version_ids), 2)
        employee_version = employee6.version_id
        self.assertEqual(employee_version.date_version, date(2022, 10, 10))
        self.assertEqual(employee_version.contract_date_start, date(2022, 10, 10))
        self.assertEqual(employee_version.wage, 3000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, team_leader_job)
        self.assertEqual(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertEqual(employee_version.trial_date_end, date(2023, 1, 10))
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(days=1))

        employee_version = employee6.with_context(active_test=False).version_ids - employee_version
        self.assertTrue(employee_version.active, "The draft contract should be converted into an archived version.")
        self.assertEqual(employee_version.contract_date_start, date.today() + relativedelta(days=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertFalse(employee_version.contract_type_id)
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        self.assertTrue(employee7.version_id)
        self.assertEqual(len(employee7.with_context(active_test=False).version_ids), 2)
        employee_version = employee7.version_id
        self.assertEqual(employee_version.date_version, date.today())
        self.assertEqual(employee_version.contract_date_start, date.today())
        self.assertEqual(employee_version.wage, 3000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, team_leader_job)
        self.assertEqual(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertEqual(employee_version.trial_date_end, date.today() + relativedelta(months=1))
        self.assertFalse(employee_version.contract_date_end)

        employee_version = employee7.with_context(active_test=False).version_ids - employee_version
        self.assertTrue(employee_version.active, "The draft contract should be converted into an archived version.")
        self.assertEqual(employee_version.contract_date_start, date.today() - relativedelta(months=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertFalse(employee_version.contract_type_id)
        self.assertEqual(employee_version.contract_date_end, date.today() - relativedelta(days=1))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        self.assertTrue(employee8.version_id)
        self.assertEqual(len(employee8.with_context(active_test=False).version_ids), 4)
        employee_version = employee8.version_id
        self.assertEqual(employee_version.date_version, date.today())
        self.assertEqual(employee_version.contract_date_start, date.today())
        self.assertEqual(employee_version.wage, 3000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, team_leader_job)
        self.assertEqual(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertEqual(employee_version.trial_date_end, date(2023, 1, 10))
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(days=1))

        employee_version, future_employee_version = employee8.version_ids - employee_version
        self.assertTrue(employee_version.active)
        self.assertEqual(employee_version.contract_date_start, date.today() - relativedelta(months=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertEqual(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertFalse(employee_version.contract_type_id)
        self.assertEqual(employee_version.contract_date_end, date.today() - relativedelta(days=1))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        employee_version = future_employee_version
        self.assertTrue(employee_version.active, "The draft contract should be converted into an archived version.")
        self.assertEqual(employee_version.contract_date_start, date.today() + relativedelta(days=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertEqual(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertFalse(employee_version.contract_type_id)
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)

        employee_version = employee8.with_context(active_test=False).version_ids.filtered(lambda v: not v.active)
        self.assertFalse(employee_version.active, "The draft contract should be converted into an archived version.")
        self.assertEqual(employee_version.contract_date_start, date.today() + relativedelta(days=2))
        self.assertEqual(employee_version.wage, 2000)
        self.assertEqual(employee_version.structure_type_id.id, structure_type_id)
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id, developer_job)
        self.assertEqual(employee_version.resource_calendar_id, self.env.company.resource_calendar_id)
        self.assertEqual(employee_version.contract_type_id, contract_type_cdd)
        self.assertEqual(employee_version.contract_date_end, date.today() + relativedelta(months=3))
        self.assertEqual(employee_version.hr_responsible_id, self.env.user)
