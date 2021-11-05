# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.4")
class TestWebsiteModel(UpgradeCase):
    def prepare(self):
        """Ensures a website's domain is corrected during migration:
        - The trailing slashes should be removed.
        - The scheme should be added.
        """
        domains = [
            # trailing /
            ("https://www.monsite.com/", "https://www.monsite.com"),
            # no scheme
            ("www.monsite.com", "https://www.monsite.com"),
            ("monsite.com", "https://monsite.com"),
            # respect scheme
            ("https://www.monsite.com", "https://www.monsite.com"),
            ("http://www.monsite.com", "http://www.monsite.com"),
            # respect port
            ("www.monsite.com:8069", "https://www.monsite.com:8069"),
            ("www.monsite.com:8069/", "https://www.monsite.com:8069"),
            # no guess wwww
            ("monsite.com", "https://monsite.com"),
            # mix
            ("www.monsite.com/", "https://www.monsite.com"),
        ]
        websites = self.env["website"].create([{"name": expected, "domain": domain} for domain, expected in domains])
        return {"website_ids": websites.ids}

    def check(self, init):
        # Domain should have been corrected
        for website in self.env["website"].browse(init["website_ids"]):
            self.assertEqual(website.name, website.domain)
