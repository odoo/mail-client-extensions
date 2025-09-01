from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.4")
class TestMigrateEmployee(UpgradeCase):
    def prepare(self):
        calendar = self.env["resource.calendar"].create(
            {"name": "Main Company Calendar", "company_id": self.env.company.id, "tz": "UTC"}
        )
        department = self.env["hr.department"].create({"name": "R&D"})
        job = self.env["hr.job"].create({"name": "Developer"})
        work_address = self.env["res.partner"].create(
            {
                "name": "Employee",
                "street": "Place du Marais",
                "zip": "5590",
                "city": "Ciney",
                "phone": "123456",
            }
        )
        work_location = self.env["hr.work.location"].create(
            {
                "name": "Odoo Ciney",
                "location_type": "office",
                "address_id": work_address.id,
            }
        )
        be_country = self.env["res.country"].search([("code", "=", "BE")])
        if not be_country:
            be_country = self.env["res.country"].create({"name": "Belgium", "code": "BE"})
        bank_bnp = self.env["res.bank"].create({"name": "BNP Paribas", "bic": "GEBABEBB"})
        bank = self.env["res.partner.bank"].create(
            {
                "acc_type": "iban",
                "acc_number": "BE15001559627230",
                "bank_id": bank_bnp.id,
                "partner_id": self.env.company.partner_id.id,
                "company_id": self.env.company.id,
            }
        )
        employee, archived_employee = self.env["hr.employee"].create(
            [
                {
                    "name": "Employee",
                    "color": 1,
                    "department_id": department.id,
                    "job_id": job.id,
                    "address_id": work_address.id,
                    "country_id": be_country.id,
                    "work_location_id": work_location.id,
                    "marital": "married",
                    "birthday": "1990-12-05",
                    "ssnid": "111111111",
                    "sinid": "2222",
                    "identification_id": "3333",
                    "passport_id": "4444",
                    "bank_account_id": bank.id,
                    "permit_no": "5555",
                    "visa_no": "6666",
                    "visa_expire": date.today() + relativedelta(years=1),
                    "additional_note": "Additional note",
                    "certificate": "master",
                    "study_field": "Computer Science",
                    "study_school": "UMons",
                    "emergency_contact": "Georges",
                    "emergency_phone": "7777",
                    "distance_home_work": "20",
                    "barcode": "8888",
                    "pin": "9999",
                    "private_car_plate": "1-AAA-123",
                    "resource_calendar_id": calendar.id,
                    "gender": "female",
                    "private_street": "Rue du Tige",
                    "private_street2": "Private street 2",
                    "private_city": "Sovet",
                    "private_zip": "5590",
                    "spouse_complete_name": "Spouse V",
                    "spouse_birthdate": "1990-12-12",
                    "children": 3,
                },
                {
                    "name": "Archived Employee",
                    "gender": "male",
                    "active": False,
                    "resource_calendar_id": False,
                    "marital": "single",
                    "employee_type": "freelance",
                },
            ]
        )
        archived_employee.write({"parent_id": employee.id, "coach_id": employee.id})
        employees = employee + archived_employee
        return [
            employees.ids,
            employees.resource_id.ids,
            calendar.id,
            job.id,
            department.id,
            work_address.id,
            work_location.id,
            be_country.id,
            bank.id,
        ]

    def check(self, init):
        (
            employee_ids,
            resource_ids,
            calendar_id,
            job_id,
            department_id,
            work_address_id,
            work_location_id,
            be_country_id,
            bank_id,
        ) = init
        employee, archived_employee = self.env["hr.employee"].browse(employee_ids)
        self.assertTrue((employee + archived_employee).exists(), "Both employees should still exist after migration")
        self.assertTrue(employee.version_id, "A version should exist for that employee")
        self.assertEqual(len(employee.version_ids), 1)
        self.assertTrue(employee.active)
        self.assertEqual(employee.name, "Employee")
        self.assertEqual(employee.color, 1)
        self.assertEqual(employee.birthday, date(1990, 12, 5))
        if util.version_gte("saas~18.5"):
            self.assertIn(bank_id, employee.bank_account_ids.ids)
        else:
            self.assertEqual(employee.bank_account_id.id, bank_id)
        self.assertEqual(employee.permit_no, "5555")
        self.assertEqual(employee.visa_no, "6666")
        self.assertEqual(employee.visa_expire, date.today() + relativedelta(years=1))
        self.assertEqual(employee.additional_note, "Additional note")
        self.assertEqual(employee.certificate, "master")
        self.assertEqual(employee.study_field, "Computer Science")
        self.assertEqual(employee.study_school, "UMons")
        self.assertEqual(employee.emergency_contact, "Georges")
        self.assertEqual(employee.emergency_phone, "7777")
        self.assertEqual(employee.barcode, "8888")
        self.assertEqual(employee.pin, "9999")
        self.assertEqual(employee.private_car_plate, "1-AAA-123")
        self.assertEqual(employee.company_id, self.env.company)
        self.assertEqual(employee.resource_id.id, resource_ids[0])

        employee_version = employee.version_id
        self.assertTrue(employee_version.active)
        self.assertTrue(employee_version.date_version, employee.create_date)
        self.assertFalse(employee_version.contract_date_start)
        self.assertFalse(employee_version.contract_date_end)
        self.assertEqual(employee_version.country_id.id, be_country_id)
        self.assertEqual(employee_version.resource_calendar_id.id, calendar_id)
        self.assertEqual(employee_version.ssnid, "111111111")
        self.assertEqual(employee_version.identification_id, "3333")
        self.assertEqual(employee_version.passport_id, "4444")
        self.assertEqual(employee_version.sex, "female")
        self.assertEqual(employee_version.private_street, "Rue du Tige")
        self.assertEqual(employee_version.private_street2, "Private street 2")
        self.assertEqual(employee_version.private_city, "Sovet")
        self.assertEqual(employee_version.private_zip, "5590")
        self.assertEqual(employee_version.distance_home_work, 20)
        self.assertEqual(employee_version.distance_home_work_unit, "kilometers")
        self.assertEqual(employee_version.marital, "married")
        self.assertEqual(employee_version.spouse_complete_name, "Spouse V")
        self.assertEqual(employee_version.spouse_birthdate, date(1990, 12, 12))
        self.assertEqual(employee_version.children, 3)
        self.assertEqual(employee_version.employee_type, "employee")
        self.assertEqual(employee_version.department_id.id, department_id)
        self.assertEqual(employee_version.job_id.id, job_id)
        self.assertEqual(employee_version.address_id.id, work_address_id)
        self.assertEqual(employee_version.work_location_id.id, work_location_id)
        self.assertFalse(employee_version.is_flexible)
        self.assertFalse(employee_version.is_fully_flexible)

        self.assertTrue(archived_employee.version_id, "A version should exist for that employee")
        self.assertEqual(len(archived_employee.version_ids), 1)
        self.assertFalse(archived_employee.active)
        self.assertEqual(archived_employee.resource_id.id, resource_ids[1])
        self.assertEqual(archived_employee.parent_id, employee)
        self.assertEqual(archived_employee.coach_id, employee)

        archived_employee_version = archived_employee.version_id
        self.assertTrue(archived_employee_version.active)
        self.assertTrue(archived_employee_version.sex, "male")
        self.assertTrue(archived_employee_version.employee_type, "freelance")
