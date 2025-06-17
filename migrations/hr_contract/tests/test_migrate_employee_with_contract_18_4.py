from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.4")
class TestMigrateEmployeeWithContract(UpgradeCase):
    def prepare(self):
        calendar = self.env["resource.calendar"].create(
            {"name": "Main Company Calendar", "company_id": self.env.company.id, "tz": "UTC"}
        )
        developer_job, team_leader_job = self.env["hr.job"].create(
            [
                {"name": "Developer"},
                {"name": "Team Leader"},
            ]
        )
        employees = employee1, employee2, employee3, employee4, employee5, employee6, employee7, employee8 = self.env[
            "hr.employee"
        ].create(
            [
                {
                    "name": "Employee with one running contract",
                    "resource_calendar_id": calendar.id,
                    "notes": "Coucou",
                    "job_id": developer_job.id,
                },
                {"name": "Employee with one draft contract", "resource_calendar_id": calendar.id, "notes": "Coucou"},
                {
                    "name": "Employee with one draft ready contract",
                    "resource_calendar_id": calendar.id,
                    "notes": "Coucou",
                },
                {"name": "Employee with one expired contract", "resource_calendar_id": calendar.id, "notes": "Coucou"},
                {
                    "name": "Employee with 2 contracts (running + draft)",
                    "resource_calendar_id": calendar.id,
                    "notes": "Coucou",
                },
                {
                    "name": "Employee with 2 contracts (running + draft ready)",
                    "resource_calendar_id": calendar.id,
                    "notes": "Coucou",
                },
                {
                    "name": "Employee with 2 contracts (running + expired)",
                    "resource_calendar_id": calendar.id,
                    "notes": "Coucou",
                },
                {
                    "name": "Employee with 4 contracts (running + expired + draft + draft running)",
                    "resource_calendar_id": calendar.id,
                    "notes": "Coucou",
                },
            ]
        )
        structure_type = self.env["hr.payroll.structure.type"].create(
            {
                "name": "Upgrade Structure type",
            }
        )
        department = self.env["hr.department"].create({"name": "R&D"})
        contract_type_cdd, contract_type_cdi = self.env["hr.contract.type"].create(
            [
                {
                    "name": "CDD",
                },
                {
                    "name": "CDI",
                },
            ]
        )
        contracts = self.env["hr.contract"].create(
            [
                {
                    "name": "UPGRADE_saas18.4-contract_template",
                    "date_start": date.today(),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "resource_calendar_id": calendar.id,
                    "notes": "Contract Template",
                    "trial_date_end": date.today() + relativedelta(months=1),
                    "date_end": date.today() + relativedelta(months=3),
                    "contract_type_id": contract_type_cdd.id,
                    "hr_responsible_id": self.env.user.id,
                },
                {
                    "name": "Contract employee 1",
                    "date_start": "2022-10-10",
                    "wage": 3000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": team_leader_job.id,
                    "notes": "Contract running",
                    "trial_date_end": "2023-01-10",
                    "date_end": False,
                    "contract_type_id": contract_type_cdi.id,
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee1.id,
                    "state": "open",
                    "resource_calendar_id": False,
                },
                {
                    "name": "Contract employee 2",
                    "date_start": date.today() + relativedelta(days=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract Draft",
                    "contract_type_id": contract_type_cdd.id,
                    "date_end": date.today() + relativedelta(months=3),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee2.id,
                },
                {
                    "name": "Contract employee 3",
                    "date_start": date.today() + relativedelta(days=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "resource_calendar_id": calendar.id,
                    "notes": "Contract ready",
                    "date_end": date.today() + relativedelta(months=3),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee3.id,
                    "kanban_state": "done",
                    "contract_type_id": None,
                },
                {
                    "name": "Contract employee 4",
                    "date_start": date.today() - relativedelta(months=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract expired",
                    "date_end": date.today() - relativedelta(days=1),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee4.id,
                    "state": "close",
                    "contract_type_id": None,
                },
                {
                    "name": "Contract employee 5",
                    "date_start": "2022-10-10",
                    "wage": 3000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": team_leader_job.id,
                    "notes": "Contract running",
                    "trial_date_end": "2023-01-10",
                    "date_end": False,
                    "contract_type_id": contract_type_cdi.id,
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee5.id,
                    "state": "open",
                },
                {
                    "name": "Contract employee 5",
                    "date_start": date.today() + relativedelta(days=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "resource_calendar_id": calendar.id,
                    "notes": "Contract Draft",
                    "contract_type_id": contract_type_cdd.id,
                    "date_end": date.today() + relativedelta(months=3),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee5.id,
                },
                {
                    "name": "Contract employee 6",
                    "date_start": "2022-10-10",
                    "wage": 3000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": team_leader_job.id,
                    "notes": "Contract running",
                    "trial_date_end": "2023-01-10",
                    "date_end": date.today() + relativedelta(days=1),
                    "contract_type_id": contract_type_cdi.id,
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee6.id,
                    "state": "open",
                },
                {
                    "name": "Contract employee 6",
                    "date_start": date.today() + relativedelta(days=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract ready",
                    "date_end": date.today() + relativedelta(months=3),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee6.id,
                    "kanban_state": "done",
                    "contract_type_id": None,
                },
                {
                    "name": "Contract employee 7",
                    "date_start": date.today() - relativedelta(months=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract expired",
                    "date_end": date.today() - relativedelta(days=1),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee7.id,
                    "state": "close",
                    "contract_type_id": None,
                },
                {
                    "name": "Contract employee 7",
                    "date_start": date.today(),
                    "wage": 3000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": team_leader_job.id,
                    "notes": "Contract running",
                    "trial_date_end": date.today() + relativedelta(months=1),
                    "date_end": False,
                    "contract_type_id": contract_type_cdi.id,
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee7.id,
                    "state": "open",
                },
                {
                    "name": "Contract employee 8",
                    "date_start": date.today() - relativedelta(months=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract expired",
                    "date_end": date.today() - relativedelta(days=1),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee8.id,
                    "state": "close",
                    "contract_type_id": None,
                },
                {
                    "name": "Contract employee 8",
                    "date_start": date.today(),
                    "wage": 3000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": team_leader_job.id,
                    "notes": "Contract running",
                    "trial_date_end": "2023-01-10",
                    "date_end": date.today() + relativedelta(days=1),
                    "contract_type_id": contract_type_cdi.id,
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee8.id,
                    "state": "open",
                },
                {
                    "name": "Contract employee 8",
                    "date_start": date.today() + relativedelta(days=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract Draft",
                    "contract_type_id": contract_type_cdd.id,
                    "date_end": date.today() + relativedelta(months=3),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee8.id,
                },
                {
                    "name": "Contract employee 8",
                    "date_start": date.today() + relativedelta(days=2),
                    "wage": 2000,
                    "structure_type_id": structure_type.id,
                    "department_id": department.id,
                    "job_id": developer_job.id,
                    "notes": "Contract ready",
                    "date_end": date.today() + relativedelta(months=3),
                    "hr_responsible_id": self.env.user.id,
                    "employee_id": employee8.id,
                    "kanban_state": "done",
                    "contract_type_id": None,
                },
            ]
        )
        return [
            employees.ids,
            len(contracts),
            calendar.id,
            department.id,
            (developer_job + team_leader_job).ids,
            structure_type.id,
            (contract_type_cdi + contract_type_cdd).ids,
        ]

    def check(self, init):
        # done in migrations/hr/tests/test_migrate_employee_with_contract.py
        return
