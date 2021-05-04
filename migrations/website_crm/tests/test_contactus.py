# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

"""
!! This test is inside `website_crm` but also ensure a correct migration of both
the `website` and `website_form` module's contactus records.
Having the test here is more convenient as we can check the migration of the
contactus records in the three modules at once.
"""


@change_version("14.5")
class TestContactus(UpgradeCase):
    def prepare(self):
        """Creates 5 websites with different COW possibilities:

                                                    | website 1 | website 2 | website 3 | website 4 | website 5 |
        website.contactus                           |           |     +     |           |     +     |           |
          website_form.contactus_form               |           |     +     |           |     +     |           |
            website_crm.contactus_form              |           |     +     |           |     +     |      +    |
        website_form.contactus_thanks               |     +     |     +     |           |           |           |
          website_form.[..]_oe_structure_[..]_1     |     +     |     +     |           |           |           |
          website_form.[..]_oe_structure_[..]_2     |     +     |     +     |           |           |           |
        website.company_description                 |           |     +     |           |           |           |
          website.company_description_google_map    |           |     +     |           |           |           |

        After migration, every website should have a copy of `/contactus`
        and `/contactus-thank-you` untouched.
        """
        Website = self.env["website"]
        website_1 = Website.create({"name": "website 1"})
        website_2 = Website.create({"name": "website 2"})
        website_3 = Website.create({"name": "website 3"})
        website_4 = Website.create({"name": "website 4"})
        website_5 = Website.create({"name": "website 5"})

        contactus = self.env.ref("website.contactus")
        params = (
            "<p>%s</p>",
            '//section[contains(@class, "s_text_block")]//p',
        )
        contactus.with_context(website_id=website_4.id).save(params[0] % website_4.name, params[1])
        contactus.with_context(website_id=website_2.id).save(params[0] % website_2.name, params[1])

        contactus_crm = self.env.ref("website_crm.contactus_form")
        contactus_crm.with_context(website_id=website_5.id).save(
            '<span class="s_website_form_label_content">%s</span>' % website_5.name,
            '(//span[contains(@class, "s_website_form_label_content")])[1]',
        )

        def cow_contactus_thank_you(website):
            contactus_thanks = self.env.ref("website_form.contactus_thanks").view_id
            contactus_thanks.with_context(website_id=website.id).save(
                '<div class="oe_structure" id="oe_structure_website_form_contact_us_thanks_1"><p>%s</p></div>'
                % website.name,
                '//div[@id="oe_structure_website_form_contact_us_thanks_1"]',
            )
            contactus_thanks.with_context(website_id=website.id).save(
                '<div class="oe_structure" id="oe_structure_website_form_contact_us_thanks_2"><p>%s</p></div>'
                % website.name,
                '//div[@id="oe_structure_website_form_contact_us_thanks_2"]',
            )
            contactus_thanks.with_context(website_id=website.id).save(
                "<h1>%s</h1>" % website.name,
                "//h1",
            )

        cow_contactus_thank_you(website_1)
        cow_contactus_thank_you(website_2)
        company_desc = self.env.ref("website.company_description")
        company_desc.with_context(website_id=website_2.id).save(
            "<a>%s</a>" % website_2.name,
            "(//a)[1]",
        )

        def get_cow_view_keys(website_id):
            recs = self.env["ir.ui.view"].search_read(
                [
                    ("website_id", "=", website_id),
                    ("key", "!=", "website.homepage"),  # bootstraped page
                ],
                ["key"],
                order="key",
            )
            return [r["key"] for r in recs]

        self.assertEqual(
            get_cow_view_keys(website_1.id),
            [
                "website_form.contactus_thanks",
                "website_form.contactus_thanks_oe_structure_website_form_contact_us_thanks_1",
                "website_form.contactus_thanks_oe_structure_website_form_contact_us_thanks_2",
            ],
        )
        self.assertEqual(
            get_cow_view_keys(website_2.id),
            [
                "website.company_description",
                "website.company_description_google_map",
                "website.contactus",
                "website_crm.contactus_form",
                "website_form.contactus_form",
                "website_form.contactus_thanks",
                "website_form.contactus_thanks_oe_structure_website_form_contact_us_thanks_1",
                "website_form.contactus_thanks_oe_structure_website_form_contact_us_thanks_2",
            ],
        )
        self.assertEqual(get_cow_view_keys(website_3.id), [])
        self.assertEqual(
            get_cow_view_keys(website_4.id),
            ["website.contactus", "website_crm.contactus_form", "website_form.contactus_form"],
        )
        self.assertEqual(get_cow_view_keys(website_5.id), ["website_crm.contactus_form"])
        self.assertFalse(
            self.env["ir.ui.view"].search_count([("type", "=", "qweb"), ("arch_db", "like", "/webite\\_form/")])
        )
        return {"1": website_1.id, "2": website_2.id, "3": website_3.id, "4": website_4.id, "5": website_5.id}

    def check(self, init):
        Website = self.env["website"]
        website_1 = Website.browse(init["1"])
        website_2 = Website.browse(init["2"])
        website_4 = Website.browse(init["4"])
        website_5 = Website.browse(init["5"])

        def get_view_wids(key):
            recs = self.env["ir.ui.view"].search_read([("type", "=", "qweb"), ("key", "=", key)], ["website_id"])
            return set([r["website_id"] and r["website_id"][0] for r in recs])

        self.assertEqual(get_view_wids("website.contactus"), set([False]))
        self.assertEqual(get_view_wids("website.contactus_migration_old"), set([False, website_2.id, website_4.id]))
        self.assertEqual(
            get_view_wids("website.contactus_form_migration_old"), set([False, website_2.id, website_4.id])
        )
        self.assertEqual(
            get_view_wids("website_crm.contactus_form_migration_old"),
            set([False, website_2.id, website_4.id, website_5.id]),
        )
        self.assertEqual(get_view_wids("website.contactus_thanks"), set([False]))
        self.assertEqual(
            get_view_wids("website.contactus_thanks_migration_old"), set([False, website_1.id, website_2.id])
        )
        self.assertEqual(
            get_view_wids("website.contactus_thanks_oe_structure_website_form_contact_us_thanks_1_migration_old"),
            set([website_1.id, website_2.id]),
        )
        self.assertEqual(
            get_view_wids("website.contactus_thanks_oe_structure_website_form_contact_us_thanks_2_migration_old"),
            set([website_1.id, website_2.id]),
        )

        def get_page_wids(url):
            recs = self.env["website.page"].search_read([("url", "=", url)], ["website_id"])
            return set([r["website_id"] and r["website_id"][0] for r in recs])

        self.assertTrue(
            get_page_wids("/contactus") == get_page_wids("/contactus-thank-you") == set([False]),
            "Only one generic page should have been created.",
        )
        self.assertEqual(get_page_wids("/migration-old-contactus"), set([False, website_2.id, website_4.id]))
        self.assertEqual(get_page_wids("/migration-old-contactus-thank-you"), set([False, website_1.id, website_2.id]))

        def get_combined_arch(website_id, key):
            return Website.with_context(website_id=website_id).viewref(key).get_combined_arch()

        for website in Website.browse(init.values()):
            # Ensure render do not crash (no xpath error/no unexisting t-call, etc).
            arch_1 = get_combined_arch(website.id, "website.contactus")
            arch_2 = get_combined_arch(website.id, "website.contactus_migration_old")
            arch_3 = get_combined_arch(website.id, "website.contactus_thanks")
            arch_4 = get_combined_arch(website.id, "website.contactus_thanks_migration_old")
            if website.id == website_2.id:  # this website COWed every views
                self.assertFalse(website.name in arch_1)
                self.assertFalse(website.name in arch_3)
                self.assertTrue(website.name in arch_2)
                self.assertTrue(website.name in arch_4)
