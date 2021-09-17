# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestICPToDomain(UpgradeCase):
    def prepare(self):
        self.env["ir.config_parameter"].set_param("mail.catchall.domain", "test.migration.com")
        self.env["ir.config_parameter"].set_param("mail.bounce.alias", "migrate+bounce")
        self.env["ir.config_parameter"].set_param("mail.catchall.alias", "migrate+catchall")
        self.env["ir.config_parameter"].set_param("mail.default.from", "migrate+default_from")
        return {}

    def check(self, init):
        alias_domain = self.env["mail.alias.domain"].search([])
        self.assertTrue(alias_domain)
        self.assertEqual(alias_domain.name, "test.migration.com")
        self.assertEqual(alias_domain.bounce_alias, "migrate+bounce")
        self.assertEqual(alias_domain.catchall_alias, "migrate+catchall")
        self.assertEqual(alias_domain.default_from, "migrate+default_from")
        companies = self.env["res.company"].search([])
        for company in companies:
            self.assertEqual(company.alias_domain_id, alias_domain)
