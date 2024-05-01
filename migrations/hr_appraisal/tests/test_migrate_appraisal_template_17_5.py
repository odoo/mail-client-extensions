from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestMigrateAppraisalTemplate(UpgradeCase):
    def prepare(self):
        company_1, company_2 = self.env["res.company"].create([{"name": "Test Company 1"}, {"name": "Test Company 2"}])

        company_1.write(
            {
                "appraisal_employee_feedback_template": "<h1>Test Company 1 Employee Template</h1>",
                "appraisal_manager_feedback_template": "<h1>Test Company 1 Manager Template</h1>",
            }
        )

        department_1, department_2, department_3 = self.env["hr.department"].create(
            [
                {
                    "name": "Department 1",
                    "custom_appraisal_templates": True,
                    "employee_feedback_template": "<h1>Department 1 Emloyee Template</h1>",
                    "manager_feedback_template": "<h1>Department 1 Manager Template</h1>",
                },
                {
                    "name": "Department 2",
                    "custom_appraisal_templates": True,
                    "employee_feedback_template": "<h1>Department 2 Emloyee Template</h1>",
                    "manager_feedback_template": "<h1>Department 2 Manager Template</h1>",
                },
                {
                    "name": "Department 3",
                    "custom_appraisal_templates": False,
                    "company_id": company_1.id,
                },
            ]
        )

        return {
            "department": [department_1.id, department_2.id, department_3.id],
            "company": [company_1.id, company_2.id],
        }

    def check(self, init):
        company_ids = self.env["res.company"].browse(init["company"])
        company_template_data = [
            (
                "Default Template (Test Company 1)",
                "<h1>Test Company 1 Employee Template</h1>",
                "<h1>Test Company 1 Manager Template</h1>",
            ),
            ("Default Template (Test Company 2)", None, None),
        ]

        for company, (template_name, emp_template, mgr_template) in zip(company_ids, company_template_data):
            self.assertEqual(company.appraisal_template_id.description, template_name)
            if emp_template:
                self.assertEqual(company.appraisal_template_id.appraisal_employee_feedback_template, emp_template)
            if mgr_template:
                self.assertEqual(company.appraisal_template_id.appraisal_manager_feedback_template, mgr_template)

        department_ids = self.env["hr.department"].browse(init["department"])
        department_template_data = [
            (
                "Department 1 Template",
                "<h1>Department 1 Emloyee Template</h1>",
                "<h1>Department 1 Manager Template</h1>",
            ),
            (
                "Department 2 Template",
                "<h1>Department 2 Emloyee Template</h1>",
                "<h1>Department 2 Manager Template</h1>",
            ),
            (
                "Default Template (Test Company 1)",
                "<h1>Test Company 1 Employee Template</h1>",
                "<h1>Test Company 1 Manager Template</h1>",
            ),
        ]

        for department, (template_name, emp_template, mgr_template) in zip(department_ids, department_template_data):
            self.assertTrue(department.custom_appraisal_template_id)
            self.assertEqual(department.custom_appraisal_template_id.description, template_name)
            self.assertEqual(department.custom_appraisal_template_id.appraisal_employee_feedback_template, emp_template)
            self.assertEqual(department.custom_appraisal_template_id.appraisal_manager_feedback_template, mgr_template)
