# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestMigrateActivityPlan(UpgradeCase):
    def prepare(self):
        # Prepare data to test plan migration
        activity_type_todo = self.env.ref("mail.mail_activity_data_todo")
        activity_type_call = self.env.ref("mail.mail_activity_data_call")
        company_b = self.env["res.company"].create({"name": "Company B test_migration_activity_plan"})
        user, user_company_b = self.env["res.users"].create(
            [
                {
                    "name": "test_user_std",
                    "login": "test_user_std",
                },
                {
                    "name": "test_user_companyb",
                    "login": "test_user_companyb",
                    "company_id": company_b.id,
                    "company_ids": [(4, company_b.id)],
                },
            ]
        )
        department_a, department_b = self.env["hr.department"].create([{"name": "dep a"}, {"name": "dep b"}])
        big_plan_activity_templates_values = [
            {
                "activity_type_id": activity_type_todo.id,
                "note": "<p>Note 1</p>",
                "responsible": "coach",
                "responsible_id": False,
                "summary": "Task 1",
            },
            {
                "activity_type_id": activity_type_todo.id,
                "note": "<p>Note 2</p>",
                "responsible": "manager",
                "responsible_id": False,
                "summary": "Task 2",
            },
            {
                "activity_type_id": activity_type_todo.id,
                "note": "<p>Note 3</p>",
                "responsible": "employee",
                "responsible_id": False,
                "summary": "Task 3",
            },
            {
                "activity_type_id": activity_type_call.id,
                "note": "<p>Note 4</p>",
                "responsible": "other",
                "responsible_id": user.id,
                "summary": "Task 4",
            },
        ]
        big_plan_values = {
            "name": "test_migration_activity_plan_Big plan with various activities",
            "department_id": department_a.id,
        }
        non_active_plan_values = {
            "name": "test_migration_activity_plan_Non active plan",
            "active": False,
            "department_id": department_b.id,
        }
        non_active_plan_activity_templates_values = [
            {
                "activity_type_id": activity_type_call.id,
                "note": "<p>Note 1</p>",
                "responsible": "coach",
                "responsible_id": False,
                "summary": "Task 1",
            }
        ]
        no_department_plan_values = {
            "company_id": company_b.id,
            "name": "test_migration_activity_plan_No department",
            "department_id": False,
        }
        no_department_plan_activity_templates_values = [
            {
                "activity_type_id": activity_type_todo.id,
                "company_id": company_b.id,
                "note": "<p>Note 1</p>",
                "responsible": "other",
                "responsible_id": user_company_b.id,
                "summary": "Task 1",
            }
        ]
        self.env["hr.plan"].create(
            [
                {
                    **big_plan_values,
                    "plan_activity_type_ids": [
                        (0, 0, activity_template_values)
                        for activity_template_values in big_plan_activity_templates_values
                    ],
                },
                {
                    **non_active_plan_values,
                    "plan_activity_type_ids": [
                        (0, 0, activity_template_values)
                        for activity_template_values in non_active_plan_activity_templates_values
                    ],
                },
                {
                    **no_department_plan_values,
                    "plan_activity_type_ids": [
                        (0, 0, activity_template_values)
                        for activity_template_values in no_department_plan_activity_templates_values
                    ],
                },
            ]
        )

        # Prepare data for hr.plan.employee.activity (introduced in 16.3) reassignment to hr.employee
        if "hr.plan.employee.activity" in self.env:
            employee = self.env["hr.employee"].create(
                {
                    "name": "employee_plan_test_16_5",
                    "user_id": self.env["res.users"]
                    .create(
                        {
                            "name": "employee_plan_test_16_5",
                            "login": "employee_plan_test_16_5",
                            "email": "employee_plan_test_16_5@example.com",
                        }
                    )
                    .id,
                }
            )
            pseudo_employee = self.env["hr.plan.employee.activity"].create({"employee_id": employee.id})
            activity_on_pseudo_employee = pseudo_employee.activity_schedule(
                "mail.mail_activity_data_todo", summary="test activity on pseudo employee"
            )
            partner = self.env["res.partner"].create({"name": "test standard"})
            activity_on_partner = partner.activity_schedule(
                "mail.mail_activity_data_todo", summary="test activity on standard record"
            )
            reassign_test = {
                "activity_on_pseudo_employee_id": activity_on_pseudo_employee.id,
                "employee_id": employee.id,
                "activity_on_partner_id": activity_on_partner.id,
                "partner_id": partner.id,
            }
        else:
            reassign_test = None

        return {
            "reassign_test": reassign_test,
            "plans": [
                {
                    "plan_values": big_plan_values,
                    "plan_activity_templates_values": big_plan_activity_templates_values,
                },
                {
                    "plan_values": non_active_plan_values,
                    "plan_activity_templates_values": non_active_plan_activity_templates_values,
                },
                {
                    "plan_values": no_department_plan_values,
                    "plan_activity_templates_values": no_department_plan_activity_templates_values,
                },
            ],
        }

    def check(self, init):
        # Test plan migration
        renamed_field = {"responsible": "responsible_type"}
        Plan = self.env["mail.activity.plan"].with_context(active_test=False)
        for data in init["plans"]:
            plan = Plan.search([("name", "=", data["plan_values"]["name"])])
            self.assertEqual(len(plan), 1)
            for record, values in (
                (plan, data["plan_values"]),
                *zip(sorted(plan.template_ids, key=lambda r: r.summary), data["plan_activity_templates_values"]),
            ):
                for field, expected_value in values.items():
                    field_dst = renamed_field[field] if field in renamed_field else field
                    comment = f"field: {field_dst}"
                    if expected_value is False:
                        self.assertFalse(record[field_dst], comment)
                    else:
                        actual_value = record[field_dst].id if isinstance(expected_value, int) else record[field_dst]
                        self.assertEqual(actual_value, expected_value, comment)
                self.assertEqual(plan.res_model, "hr.employee")

        # Test hr.plan.employee.activity reassignment to hr.employee
        data = init["reassign_test"]
        if data:
            activity_on_pseudo_employee = self.env["mail.activity"].browse([data["activity_on_pseudo_employee_id"]])
            self.assertEqual(activity_on_pseudo_employee.res_model, "hr.employee")
            self.assertEqual(activity_on_pseudo_employee.res_id, data["employee_id"])
            self.assertEqual(activity_on_pseudo_employee.res_model_id, self.env.ref("hr.model_hr_employee"))
            # Test that other activities are not affected by the reassignment
            activity_on_partner = self.env["mail.activity"].browse([data["activity_on_partner_id"]])
            self.assertEqual(activity_on_partner.res_model, "res.partner")
            self.assertEqual(activity_on_partner.res_id, data["partner_id"])
            self.assertEqual(activity_on_partner.res_model_id, self.env.ref("base.model_res_partner"))
