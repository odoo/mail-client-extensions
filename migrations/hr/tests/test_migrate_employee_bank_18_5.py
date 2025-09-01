from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestMigrateEmployeeBankAccounts(UpgradeCase):
    def prepare(self):
        be_country = self.env["res.country"].search([("code", "=", "BE")], limit=1)
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
        employee = self.env["hr.employee"].create(
            {
                "name": "Employee",
                "bank_account_id": bank.id,
                "country_id": be_country.id,
            }
        )
        return [employee.id, bank.id]

    def check(self, init):
        employee_id, bank_id = init
        employee = self.env["hr.employee"].browse(employee_id)
        bank = self.env["res.partner.bank"].browse(bank_id)
        self.assertTrue(employee.exists(), "Employee should still exist after migration")
        self.assertTrue(bank.exists(), "Bank Account should still exist after migration")
        self.assertIn(
            bank_id,
            employee.bank_account_ids.ids,
            "Employee should keep their bank account after migration",
        )
