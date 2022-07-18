from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~11.3")
class ResBankPartner(UpgradeCase):
    def prepare(self):
        bank_partner = self.env["res.bank.partner"].create(
            {
                "acc_number": "XXXXX",
            },
        )
        self.assertFalse(bool(bank_partner.partner_id))
        return bank_partner.id

    def check(self, bid):
        bank_partner = self.env["res.bank.partner"].browse(bid)
        self.assertTrue(bool(bank_partner.partner_id))
