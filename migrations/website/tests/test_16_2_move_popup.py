# -*- coding: utf-8 -*-

from lxml import html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")
key_footer = "website.footer_custom"
key_shared_blocks = "website.shared_blocks"


@change_version("saas~16.2")
class TestMovePopup(UpgradeCase):
    def prepare(self):
        arch = """
        <data inherit_id="website.layout" name="Default" active="True">
            <xpath expr="//div[@id='footer']" position="replace">
                <div id="footer" class="oe_structure oe_structure_solo" t-ignore="true" t-if="not no_footer">
                    <div class="s_popup o_snippet_invisible d-none" data-vcss="001" data-snippet="s_popup"
                    data-name="Popup" id="sPopup1673368992605" data-invisible="1">
                        <h1>POPUP CONTENT</h1>
                    </div>
                </div>
            </xpath>
        </data>
        """.replace(
            r"\n", ""
        )
        generic_footer = self.env.ref(key_footer)
        Website = self.env["website"]
        self.env["res.lang"]._activate_lang("fr_BE")

        # trigger cow and change arch of the cow
        generic_footer.with_context(website_id=1, lang="en_US").arch_db = arch
        Website.with_context(website_id=1).viewref(key_footer).update_field_translations(
            "arch_db", {"fr_BE": {"POPUP CONTENT": "CONTENU DU POPUP"}}
        )

        Website.create({"name": "Website 2"})
        # Cow the generic website layout for website 2
        generic_website_layout = self.env.ref("website.layout")
        generic_website_layout.with_context(website_id=2).name = f"{generic_website_layout.name} - COW website_2"

        generic_footer.with_context(website_id=2, lang="en_US").arch_db = arch.replace(
            "POPUP CONTENT", "POPUP CONTENT w2"
        )
        Website.with_context(website_id=2).viewref(key_footer).update_field_translations(
            "arch_db", {"fr_BE": {"POPUP CONTENT w2": "CONTENU DU POPUP w2"}}
        )

    def check(self, init):
        Website = self.env["website"]
        # Website 1 views
        arch_footer_w1_en = Website.with_context(website_id=1, lang="en_US").viewref(key_footer).arch_db
        arch_footer_w1_fr = Website.with_context(website_id=1, lang="fr_BE").viewref(key_footer).arch_db
        arch_shared_blocks_w1_en = Website.with_context(website_id=1, lang="en_US").viewref(key_shared_blocks).arch_db
        arch_shared_blocks_w1_fr = Website.with_context(website_id=1, lang="fr_BE").viewref(key_shared_blocks).arch_db
        # Website 2 views
        arch_footer_w2_en = Website.with_context(website_id=2, lang="en_US").viewref(key_footer).arch_db
        arch_footer_w2_fr = Website.with_context(website_id=2, lang="fr_BE").viewref(key_footer).arch_db
        arch_shared_blocks_w2_en = Website.with_context(website_id=2, lang="en_US").viewref(key_shared_blocks).arch_db
        arch_shared_blocks_w2_fr = Website.with_context(website_id=2, lang="fr_BE").viewref(key_shared_blocks).arch_db

        tests = [
            {"arch": arch_footer_w1_en, "should_not_contain": ["s_popup", "POPUP CONTENT", "CONTENU DU POPUP", "w2"]},
            {"arch": arch_footer_w1_fr, "should_not_contain": ["s_popup", "POPUP CONTENT", "CONTENU DU POPUP", "w2"]},
            {
                "arch": arch_shared_blocks_w1_en,
                "should_not_contain": ["CONTENU DU POPUP", "w2"],
                "should_contain": ["s_popup", "POPUP CONTENT"],
            },
            {
                "arch": arch_shared_blocks_w1_fr,
                "should_not_contain": ["POPUP CONTENT", "w2"],
                "should_contain": ["s_popup", "CONTENU DU POPUP"],
            },
            {"arch": arch_footer_w2_en, "should_not_contain": ["s_popup", "POPUP CONTENT", "CONTENU DU POPUP"]},
            {"arch": arch_footer_w2_fr, "should_not_contain": ["s_popup", "POPUP CONTENT", "CONTENU DU POPUP"]},
            {
                "arch": arch_shared_blocks_w2_en,
                "should_not_contain": ["CONTENU DU POPUP"],
                "should_contain": ["s_popup", "POPUP CONTENT", "w2"],
            },
            {
                "arch": arch_shared_blocks_w2_fr,
                "should_not_contain": ["POPUP CONTENT"],
                "should_contain": ["s_popup", "CONTENU DU POPUP", "w2"],
            },
        ]
        errors = []
        for test in tests:
            for string in test["should_not_contain"]:
                if string in test["arch"]:
                    errors.append(f"String {string} should not be in {test['arch']}")
            for string in test.get("should_contain", []):
                if string not in test["arch"]:
                    errors.append(f"String {string} should be in {test['arch']}")

        shared_blocks_w1 = Website.with_context(website_id=1).viewref(key_shared_blocks)
        shared_blocks_w2 = Website.with_context(website_id=2).viewref(key_shared_blocks)

        if "- COW website_2" not in shared_blocks_w2.inherit_id.name:
            errors.append("The shared blocks parent view of website 2 lost its cow suffix")
        if "- COW website_2" in shared_blocks_w1.inherit_id.name:
            errors.append("The name of shared blocks parent view of website 1 should not have changed")
        if shared_blocks_w2.inherit_id.website_id.id != 2:
            errors.append("The shared blocks view of website 2 should inherit from the cowed website layout")

        self.assertEqual(len(errors), 0, "\n".join(errors))
