from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestAccountCompanies(UpgradeCase):
    def prepare(self):
        test_company = self.env["res.company"].create(
            {
                "name": "TestAccountCompanies test company",
                "parent_id": self.env.company.id,
            }
        )
        test_account = self.env["account.account"].create(
            {
                "name": "My Test Account",
                "code": "187369",
                "company_id": test_company.id,
            }
        )

        return {
            "test_company_id": test_company.id,
            "test_account_id": test_account.id,
        }

    def check(self, init):
        test_account = self.env["account.account"].browse(init["test_account_id"])
        self.assertRecordValues(test_account, [{"code": "187369", "company_ids": [init["test_company_id"]]}])
