# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestMigrateActivityPlan(UpgradeCase):

    def prepare(self):
        single_page_pdf = b"JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDIzMDMxNTE1MTA1MS0wMScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjMwMzE1MTUxMDUxLTAxJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3BlY2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCA1OQo+PgpzdHJlYW0KR2FwUWgwRT1GLDBVXEgzVFxwTllUXlFLaz90Yz5JUCw7VyNVMV4yM2loUEVNX1BQJE8hM14sQzVRfj5lbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA4CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDA3MyAwMDAwMCBuIAowMDAwMDAwMTA0IDAwMDAwIG4gCjAwMDAwMDAyMTEgMDAwMDAgbiAKMDAwMDAwMDQxNCAwMDAwMCBuIAowMDAwMDAwNDgyIDAwMDAwIG4gCjAwMDAwMDA3NzggMDAwMDAgbiAKMDAwMDAwMDgzNyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9JRCAKWzwwZDY3YWVkODM1MGJkYjViNGJhY2M5MGU5MTg0ODBjYj48MGQ2N2FlZDgzNTBiZGI1YjRiYWNjOTBlOTE4NDgwY2I+XQolIFJlcG9ydExhYiBnZW5lcmF0ZWQgUERGIGRvY3VtZW50IC0tIGRpZ2VzdCAoaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tKQoKL0luZm8gNSAwIFIKL1Jvb3QgNCAwIFIKL1NpemUgOAo+PgpzdGFydHhyZWYKOTg1CiUlRU9GCg=="
        attachment = self.env["ir.attachment"].create(
            {
                "type": "binary",
                "datas": single_page_pdf,
                "name": "test_employee_contract.pdf",
            }
        )
        template_role = self.env["sign.template"].create(
            {
                "name": "hr_contract_sign_test_migration_template",
                "attachment_id": attachment.id,
            }
        )
        self.env["sign.item"].create(
            [
                {
                    "type_id": self.env.ref("sign.sign_item_type_text").id,
                    "required": True,
                    "responsible_id": self.env.ref(ref_responsible_id).id,
                    "page": 1,
                    "posX": 0.273,
                    "posY": 0.158,
                    "template_id": template_role.id,
                    "width": 0.150,
                    "height": 0.015,
                }
                for ref_responsible_id in ("sign.sign_item_role_employee", "sign.sign_item_role_company")
            ]
        )
        plan = self.env["hr.plan"].create(
            {
                "name": "hr_contract_sign_test_migration_plan",
                "plan_activity_type_ids": [(0, 0, {
                    "activity_type_id": self.env.ref("sign.mail_activity_data_signature_request").id,
                    "responsible": "employee",
                    "sign_template_id": template_role.id,
                })],
            }
        )
        return plan.ids

    def check(self, init):
        plan = self.env["mail.activity.plan"].browse(init[0])
        self.assertEqual(plan.res_model, "hr.employee")
        activity_templates = plan.template_ids[0]
        self.assertEqual(len(activity_templates), 1)
        self.assertEqual(activity_templates.sign_template_id.name, "hr_contract_sign_test_migration_template")
        self.assertFalse(activity_templates.employee_role_id)
        self.assertEqual(set(activity_templates.sign_template_responsible_ids.mapped("name")), {"Employee", "Company"})
        self.assertEqual(activity_templates.responsible_count, 2)
