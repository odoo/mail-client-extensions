from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestWebsiteControllerPageM2ORecord(UpgradeCase):
    def prepare(self):
        view = self.env["ir.ui.view"].create({"arch": "<div />", "type": "qweb", "name": "migr_test"})
        website_ct_page = self.env["website.controller.page"].create(
            {
                "model": "res.partner",
                "page_name": "slugish",
                "view_id": view.id,
                "name_slugified": "slugish",
                "page_type": "listing",
                "is_published": True,
            }
        )
        view_copy = view.copy()
        website_ct_page_copy = website_ct_page.copy(
            {"view_id": view_copy.id, "page_type": "single", "is_published": True}
        )

        view_copy = view.copy()
        website_ct_page_copy_2 = website_ct_page.copy(
            {
                "view_id": view_copy.id,
                "page_type": "single",
                "page_name": "slugish-2",
                "name_slugified": "slugish-2",
                "is_published": True,
            }
        )

        return {"page_ids": [website_ct_page.id, website_ct_page_copy.id, website_ct_page_copy_2.id]}

    def check(self, init):
        pages = self.env["website.controller.page"].browse(init["page_ids"])
        self.assertEqual(pages[0].record_view_id, pages[1].view_id)
        self.assertEqual(pages[2].view_id, pages[2].record_view_id)
        self.assertFalse(pages[2].is_published)
