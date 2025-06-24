from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class BankStatementLinePartner(UpgradeCase):
    def _get_lines_data(self, companies, partners):
        data = [
            {"partner_id": partners["p0"]},
            {"account_number": ""},
            {"account_number": "   "},
            {"account_number": "512 3", "company_id": companies["c6"]},
            {"account_number": "12 36", "company_id": companies["c6"]},
            {"account_number": "3455 ", "company_id": companies["c1"]},
            {"account_number": "345  "},
            {"account_number": "34   "},
            {"account_number": "34   ", "partner_name": "TeST3"},
            {"account_number": "34   ", "partner_name": "TeSt4", "company_id": companies["c1"]},
            {"account_number": "34   ", "partner_name": "EsT", "company_id": companies["c6"]},
            {"account_number": "34   ", "partner_name": "EsT", "company_id": companies["c3"]},
            {"account_number": "34   ", "partner_name": "TES", "company_id": companies["c2"]},
            {"account_number": "34   ", "partner_name": "TES", "company_id": companies["c0"]},
            {"account_number": "34   ", "partner_name": "ach", "company_id": companies["c4"]},
            {"account_number": "34   ", "partner_name": "ache", "company_id": companies["c4"]},
            {"account_number": "34   ", "partner_name": "ache", "company_id": companies["c5"]},
            {"partner_name": "CBC"},
            {"partner_name": "ERD"},
            {"partner_name": "DNA"},
        ]
        return [{"payment_ref": f"l{i:02}", "amount": 20, **d} for i, d in enumerate(data)]

    def prepare(self):
        companies = {"c0": self.env["res.company"].create({"name": "Parent Company Test BSLP"})}
        sus_account = self.env["account.account"].create(
            {"name": "Account", "code": "1", "account_type": "asset_current", "company_ids": [companies["c0"].id]}
        )
        self.env["account.journal"].create(
            {
                "name": "Default Journal",
                "code": "cash",
                "type": "cash",
                "company_id": companies["c0"].id,
                "suspense_account_id": sus_account.id,
            }
        )
        company_to_parent = [
            ("c1", "c0"),
            ("c2", "c0"),
            ("c3", "c0"),
            ("c4", "c3"),
            ("c5", "c4"),
            ("c6", "c5"),
        ]
        for name, parent in company_to_parent:
            parent_id = companies[parent].id if parent else None
            companies[name] = self.env["res.company"].create({"name": name, "parent_id": parent_id})

        partners = {
            f"p{i}": self.env["res.partner"].create(partner_data)
            for i, partner_data in enumerate(
                [
                    {"name": "test1", "company_id": companies["c0"].id, "active": False},
                    {"name": "test2", "company_id": companies["c0"].id},
                    {"name": "test3", "company_id": companies["c0"].id},
                    {"name": "test4", "company_id": companies["c2"].id},
                    {"name": "est", "company_id": companies["c4"].id},
                    {"name": "achen", "company_id": companies["c3"].id},
                    {"name": "ach", "company_id": companies["c4"].id},
                    {"name": "bachen", "company_id": companies["c5"].id},
                    {"name": "MBC", "company_id": companies["c0"].id},
                    {"name": "CFA", "company_id": companies["c0"].id},
                    {"name": "SNA", "company_id": companies["c0"].id},
                ]
            )
        }

        self.env["res.partner.bank"].create(
            [
                {"acc_number": "45 12 3 89", "partner_id": partners["p0"].id, "company_id": companies["c4"].id},
                {"acc_number": " 5 12 3 6 ", "partner_id": partners["p0"].id, "company_id": companies["c3"].id},
                {"acc_number": " 4 12 3 67", "partner_id": partners["p1"].id, "company_id": companies["c5"].id},
                {"acc_number": " 4 12 3 68", "partner_id": partners["p1"].id, "company_id": companies["c6"].id},
                {"acc_number": " 345      ", "partner_id": partners["p1"].id},
                {"acc_number": " 34 5     ", "partner_id": partners["p0"].id},
                {"acc_number": " 34556789 ", "partner_id": partners["p0"].id},
                {"acc_number": " 999 345 0", "partner_id": partners["p1"].id},
                {"acc_number": " 999 346 0", "partner_id": partners["p2"].id},
            ]
        )

        # reconciled lines (with amount = 0)
        self.env["account.bank.statement.line"].with_company(companies["c0"]).create(
            [
                {"partner_name": "CBC", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "CBC", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "CBC", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "CBC", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "CBC", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "ERD", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "ERD", "partner_id": partners["p9"].id, "company_id": partners["p9"].company_id.id},
                {"partner_name": "DNA", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "DNA", "partner_id": partners["p8"].id, "company_id": partners["p8"].company_id.id},
                {"partner_name": "DNA", "partner_id": partners["p10"].id, "company_id": partners["p10"].company_id.id},
                {"partner_name": "DNA", "partner_id": partners["p10"].id, "company_id": partners["p10"].company_id.id},
                {"partner_name": "DNA", "partner_id": partners["p10"].id, "company_id": partners["p10"].company_id.id},
            ]
        )

        # these lines get their partner_id computed through SQL logic in pre-bank-statement-line-partner.py
        companies_ids = {company_name: company.id for company_name, company in companies.items()}
        partners_ids = {partner_name: partner.id for partner_name, partner in partners.items()}
        lines_ids = {
            f"l{i}": self.env["account.bank.statement.line"].with_company(companies["c0"]).create(line_data).id
            for i, line_data in enumerate(self._get_lines_data(companies_ids, partners_ids))
        }

        return {"companies": companies_ids, "partners": partners_ids, "lines": lines_ids}

    def check(self, init):
        companies = init["companies"]
        partners = init["partners"]
        lines_sql = init["lines"]
        # these lines get their partner_id computed through python logic of _retrieve_partner in account_bank_statement
        lines_python = {
            f"l{i}": self.env["account.bank.statement.line"].with_company(companies["c0"]).create(line_data)
            for i, line_data in enumerate(self._get_lines_data(companies, partners))
        }
        for line_name in lines_sql:
            line_sql = self.env["account.bank.statement.line"].browse(lines_sql[line_name])
            line_python = lines_python[line_name]
            self.assertEqual(line_sql.partner_id.id, line_python.partner_id.id)
