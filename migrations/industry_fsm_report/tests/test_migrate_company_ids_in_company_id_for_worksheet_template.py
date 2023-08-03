import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.2")
class TestMigrateCompanyIdsInCompanyIdForWorksheetTemplate(UpgradeCase):
    def prepare(self):
        company1, company2 = self.env["res.company"].create([{"name": "Company 1"}, {"name": "Company 2"}])
        self.env["worksheet.template"].create(
            [
                {"name": "UPG:saas~17.2-worksheet_template-1", "res_model": "project.task"},
                {
                    "name": "UPG:saas~17.2-worksheet_template-2",
                    "res_model": "project.task",
                    "company_ids": [company1.id],
                },
                {
                    "name": "UPG:saas~17.2-worksheet_template-3",
                    "res_model": "project.task",
                    "company_ids": [company1.id, company2.id],
                },
            ]
        )
        search_view = self.env["ir.ui.view"].create(
            {
                "name": "search.view",
                "type": "search",
                "model": "worksheet.template",
                "arch": f"""
                <search>
                    <filter name="company1" domain="[('company_ids', '=', {company1.id})]"/>
                    <filter name="in_company1" domain="[('company_ids', 'in', {company1.ids})]"/>
                    <filter name="not_company1" domain="[('company_ids', '!=', {company1.id})]"/>
                    <filter name="not_in_company1" domain="[('company_ids', 'not in', {company1.ids})]"/>
                    <filter name="company2" domain="[('company_ids', '=', {company2.id})]"/>
                    <filter name="in_company2" domain="[('company_ids', 'in', {company2.ids})]"/>
                    <filter name="not_company2" domain="[('company_ids', '!=', {company2.id})]"/>
                    <filter name="not_in_company2" domain="[('company_ids', 'not in', {company2.ids})]"/>
                    <filter name="both_companies" domain="[('company_ids', 'in', [{company1.id}, {company2.id}])]"/>
                    <filter name="not_both_companies" domain="[('company_ids', 'not in', [{company1.id}, {company2.id}])]"/>
                </search>
            """,
            }
        )

        return (
            (company1 + company2).ids,
            search_view.id,
        )

    def check(self, init):
        company_ids, search_view_id = init
        company1, company2 = self.env["res.company"].browse(company_ids)
        search_view = self.env["ir.ui.view"].browse(search_view_id)
        worksheet_templates = self.env["worksheet.template"].search(
            [("name", "ilike", "UPG:saas~17.2-worksheet_template")]
        )

        worksheet_template1 = worksheet_templates.filtered(lambda t: t.name == "UPG:saas~17.2-worksheet_template-1")
        self.assertEqual(len(worksheet_template1), 1)
        self.assertFalse(worksheet_template1.company_id)

        worksheet_template2 = worksheet_templates.filtered(lambda t: t.name == "UPG:saas~17.2-worksheet_template-2")
        self.assertEqual(len(worksheet_template2), 1)
        self.assertEqual(worksheet_template2.company_id, company1)

        worksheet_template3 = worksheet_templates.filtered(lambda t: t.name == "UPG:saas~17.2-worksheet_template-3")
        self.assertEqual(len(worksheet_template3), 2)
        self.assertEqual(worksheet_template3.company_id, company1 + company2)

        # Check if the domains are correctly adapted
        # Regex to get domain attribute of each filter
        domains_regex = re.compile(r"domain=\"(.*?)\"")
        worksheet_template_domains = domains_regex.findall(search_view.arch)
        expected_worksheet_template_domains = [
            [("company_id", "=", company1.id)],
            [("company_id", "in", company1.ids)],
            [("company_id", "!=", company1.id)],
            [("company_id", "not in", company1.ids)],
            [("company_id", "=", company2.id)],
            [("company_id", "in", company2.ids)],
            [("company_id", "!=", company2.id)],
            [("company_id", "not in", company2.ids)],
            [("company_id", "in", company_ids)],
            [("company_id", "not in", company_ids)],
        ]
        for domain_str, expected_domain in zip(worksheet_template_domains, expected_worksheet_template_domains):
            domain = ast.literal_eval(domain_str.replace("domain=", ""))
            self.assertEqual(domain, expected_domain, f"Expected domain {expected_domain} but got {domain}")
