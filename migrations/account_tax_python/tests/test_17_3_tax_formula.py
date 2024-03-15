from odoo.addons.base.maintenance.migrations.account.tests.test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~17.3")
class TestTaxFormula(TestAccountingSetupCommon):

    def python_tax(self, name, formula):
        return self.env["account.tax"].create(
            {
                "name": name,
                "amount_type": "code",
                "amount": 0.0,
                "python_compute": formula,
            }
        )

    def _check_test_working_formula(self, config, tax_id):
        tax = self.env["account.tax"].browse(tax_id)
        self.assertEqual(tax.formula, "base * 2")

    def prepare(self):
        res = super().prepare()
        res["tests"].append(
            (
                "_check_test_working_formula",
                self.python_tax("test_working_formula", " result  =     base_amount * 2").ids,
            )
        )
        return res
