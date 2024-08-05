from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestRefactorAccount(UpgradeCase):
    def prepare(self):
        iap_account_reveal = self.env["iap.account"].create(
            {
                "name": "custom name",
                "service_name": "reveal",
                "account_token": "1",
            }
        )
        iap_account_reveal_no_name = self.env["iap.account"].create(
            {
                "service_name": "reveal",
                "account_token": "2",
            }
        )
        return iap_account_reveal.account_token, iap_account_reveal_no_name.account_token

    def check(self, init):
        iap_account_reveal = self.env["iap.account"].search([("account_token", "=", init[0])])
        iap_account_reveal_no_name = self.env["iap.account"].search([("account_token", "=", init[1])])

        self.assertEqual(iap_account_reveal.service_id.technical_name, "reveal")

        # Check that if the account did not have a name, it is filled using the name of the service
        self.assertEqual(iap_account_reveal_no_name.name, "Lead Generation")
        self.assertEqual(iap_account_reveal.name, "custom name")
