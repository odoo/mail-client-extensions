import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.2")
class TestMigratePriorityInIsFavorite(UpgradeCase):
    def prepare(self):
        products = self.env["product.template"].create(
            [
                {"name": "product", "priority": "0"},
                {"name": "product_in_favorite", "priority": "1"},
            ]
        )

        search_view = self.env["ir.ui.view"].create(
            {
                "name": "product.template.search",
                "type": "search",
                "model": "product.template",
                "arch": """
                <search>
                    <filter name="is_favorite" string="Is Favorite" domain="[('priority', '=', '1')]" />
                    <filter name="is_favorite_2" string="Is Favorite 2" domain="[('priority', '!=', '0')]" />
                    <filter name="not_is_favorite" string="Is Not Favorite" domain="[('priority', '!=', '1')]" />
                    <filter name="not_is_favorite_2" string="Is Not Favorite 2" domain="[('priority', '=', '0')]" />
                </search>
            """,
            }
        )

        return products.ids, search_view.id

    def check(self, init):
        product_ids, search_view_id = init
        product, product_in_favorite = self.env["product.template"].browse(product_ids)
        product_search_view = self.env["ir.ui.view"].browse(search_view_id)

        self.assertFalse(product.is_favorite)
        self.assertTrue(product_in_favorite.is_favorite)

        # Check if the domains are correctly adapted
        # Regex to get domain attribute of each filter
        domains_regex = re.compile(r"domain=\"(.*?)\"")
        product_search_view_domains = domains_regex.findall(product_search_view.arch)
        expected_product_search_view_domains = [
            [("is_favorite", "=", True)],
            [("is_favorite", "!=", False)],
            [("is_favorite", "!=", True)],
            [("is_favorite", "=", False)],
        ]
        for domain_str, expected_domain in zip(product_search_view_domains, expected_product_search_view_domains):
            domain = ast.literal_eval(domain_str)
            left, op, right = domain[0]
            expected_left, expected_op, expected_right = expected_domain[0]
            self.assertEqual(left, expected_left)
            self.assertEqual(op, expected_op)
            self.assertEqual(right, expected_right)
