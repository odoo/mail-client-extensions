# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.3")
class TestGuessCountry(UpgradeCase):
    def prepare(self):
        expectations = {}

        # Set default value for company currency, independently from the installed CoA...
        self.env["ir.default"].set("res.company", "currency_id", value=self.env.ref("base.EUR").id)

        # Clue: Partner's country (Belgium)
        c = self.env["res.company"].create({"name": "Gourmet fries import/export"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        country_id = self.env["res.country"].search([("name", "=", "Belgium")]).id
        p.country_id = country_id
        expectations[c.id] = country_id

        # Clue: Company name (Nigeria - not Niger)
        c = self.env["res.company"].create({"name": "New Nigerian Tech Solutions"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        country_id = self.env["res.country"].search([("name", "=", "Nigeria")]).id
        expectations[c.id] = country_id

        # Clue: Timezone (Slovakia)
        c = self.env["res.company"].create({"name": "Partner in Time"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        p.tz = "Europe/Bratislava"
        country_id = self.env["res.country"].search([("name", "=", "Slovakia")]).id
        expectations[c.id] = country_id

        # Clue: Phone code of company (Peru)
        c = self.env["res.company"].create({"name": "El Condor Pasta", "phone": "+51 123456789"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        country_id = self.env["res.country"].search([("name", "=", "Peru")]).id
        expectations[c.id] = country_id

        # Clue: Phone code of partner (Argentina)
        c = self.env["res.company"].create({"name": "The happy steak"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        p.phone = "+54 123456789"
        country_id = self.env["res.country"].search([("name", "=", "Argentina")]).id
        expectations[c.id] = country_id

        # Clue: Mobile phone code of partner (Mexico - not Costa Rica)
        c = self.env["res.company"].create({"name": "Sr. Frijol's restaurant", "phone": "506 607 708"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        p.phone = "+52 506 607 608"
        country_id = self.env["res.country"].search([("name", "=", "Mexico")]).id
        expectations[c.id] = country_id

        # Clue: Currency of journal (Somalia - not US or Canada)
        c = self.env["res.company"].create({"name": "Journalistic enquiries Consultancy", "phone": "+1 123456789"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        cur_id = self.env["res.country"].search([("name", "=", "Somalia")]).currency_id.id
        self.env["account.journal"].create(
            {"name": "Journal name", "code": 1, "type": "general", "company_id": c.id, "currency_id": cur_id}
        )
        country_id = self.env["res.country"].search([("name", "=", "Somalia")]).id
        expectations[c.id] = country_id

        # Clue: Currency of company (Georgia - not Eurozone country)
        cur_id = self.env["res.country"].search([("name", "=", "Georgia")]).currency_id.id
        c = self.env["res.company"].create({"name": "Andro's Beds and Furniture", "currency_id": cur_id})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        self.env["account.journal"].create(
            {"name": "Journal second name", "code": 1, "type": "general", "company_id": c.id, "currency_id": cur_id}
        )
        country_id = self.env["res.country"].search([("name", "=", "Georgia")]).id
        expectations[c.id] = country_id

        # Clue: TLD of company's email address (UK)
        c = self.env["res.company"].create({"name": "A Co. in UK", "email": "co.uk@coke.co.uk"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        country_id = self.env["res.country"].search([("name", "=", "United Kingdom")]).id
        expectations[c.id] = country_id

        # Clue: TLD of company's partner's email address (Turkey)
        c = self.env["res.company"].create({"name": "Batman", "email": "batman@cave.com"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        p.email = "bruce@batman.tr"
        country_id = self.env["res.country"].search([("name", "=", "Turkey")]).id
        expectations[c.id] = country_id

        # Clue: TLD of company's partner's website address (France)
        c = self.env["res.company"].create({"name": "Your stable investment"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        p.website = "horserider.fr"
        country_id = self.env["res.country"].search([("name", "=", "France")]).id
        expectations[c.id] = country_id

        # Clue: Language locale (Belgium)
        c = self.env["res.company"].create({"name": "Locale growth farms"})
        self.env["account.tax"].create({"name": "Test tax 25%", "company_id": c.id})
        p = c.partner_id
        self.cr.execute(
            "UPDATE res_partner SET lang='fr_BE' WHERE id=%s" % p.id
        )  # manual SQL query skips language installation
        country_id = self.env["res.country"].search([("name", "=", "Belgium")]).id
        expectations[c.id] = country_id

        return expectations

    def check(self, expectations):
        C = self.env["res.country"]
        expectations = {int(k): int(v) for k, v in expectations.items()}
        companies = self.env["res.company"].browse(expectations.keys())

        for company in companies:
            actual = company.account_fiscal_country_id.name
            expected = C.browse(expectations[company.id]).name
            self.assertEqual(actual, expected, f"Bad country match for company {company.name}")
