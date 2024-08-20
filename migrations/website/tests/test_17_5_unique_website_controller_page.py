from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestWebsiteControllerPageUnique(UpgradeCase):
    def prepare(self):
        view = self.env["ir.ui.view"].create({"arch": "<div />", "type": "qweb", "name": "migr_test"})
        website_ct_page = self.env["website.controller.page"].create(
            {
                "model": "res.partner",
                "page_name": "my page",
                "view_id": view.id,
                "name_slugified": "slugish",
                "page_type": "listing",
            }
        )
        view_copy = view.copy()
        website_ct_page_copy = website_ct_page.copy({"view_id": view_copy.id})
        self.env["website.menu"].create({"name": "menu1", "controller_page_id": website_ct_page.id})
        self.env["website.menu"].create({"name": "menu2", "controller_page_id": website_ct_page_copy.id})
        self.assertEqual(
            (website_ct_page.page_type, website_ct_page.name_slugified),
            (website_ct_page_copy.page_type, website_ct_page_copy.name_slugified),
        )
        return {"page_ids": [website_ct_page.id, website_ct_page_copy.id]}

    def check(self, init):
        pages = self.env["website.controller.page"].browse(init["page_ids"])
        self.assertTrue(pages[0].name_slugified != pages[1].name_slugified)
        for page in pages:
            url = f"/model/{page.name_slugified}"
            for menu_id in page.menu_ids:
                self.assertEqual(menu_id.url, url)
