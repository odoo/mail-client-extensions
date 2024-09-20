from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestShareMigration(UpgradeCase):
    def prepare(self):
        user = self.env["res.users"].create({"name": "Test HR", "login": "test_hr"})
        employee = self.env["hr.employee"].create({"user_id": user.id, "private_email": "test_hr@example.com"})
        employee.action_send_documents_share_link()

        share = self.env["documents.share"].search([("name", "ilike", "HR Documents")])
        return {
            "employee": employee.id,
            "share_hr": share.access_token,
        }

    def check(self, init):
        employee = self.env["hr.employee"].browse(init["employee"])
        share_hr = self.env["documents.redirect"].search([("access_token", "=", init["share_hr"])])
        self.assertEqual(share_hr.employee_id, employee)
