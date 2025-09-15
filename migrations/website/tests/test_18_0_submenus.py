import json

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("18.0")
class TestWebsiteSubmenus(UpgradeCase):
    def prepare(self):
        website = self.env.ref("website.default_website")
        Menu = self.env["website.menu"]

        mega_parent = Menu.create({"name": "Mega Parent", "website_id": website.id})
        mega_child = Menu.create({"name": "Mega Child", "parent_id": mega_parent.id, "website_id": website.id})
        # Bypass the new validation to reproduce legacy mega menu hierarchies.
        default_lang = self.env.context.get("lang", "en_US")
        # Html fields store translations as a JSON map keyed by language code.
        html_payload = json.dumps({default_lang: "<div>mega</div>"})
        self.env.cr.execute(
            "UPDATE website_menu SET mega_menu_content = %s WHERE id = %s",
            (html_payload, mega_parent.id),
        )

        root = Menu.create({"name": "Root", "website_id": website.id})
        second = Menu.create({"name": "Second", "parent_id": root.id, "website_id": website.id})
        third = Menu.create({"name": "Third", "parent_id": second.id, "website_id": website.id})
        # Fourth level is inserted via SQL to bypass the newer constraint and mimic pre-17 data.
        fourth = Menu.create({"name": "Fourth", "website_id": website.id})
        self.env.cr.execute(
            "UPDATE website_menu SET parent_id = %s WHERE id = %s",
            (third.id, fourth.id),
        )

        nested_mega = Menu.create({"name": "Nested Mega", "parent_id": second.id, "website_id": website.id})
        # Same workaround for the nested mega menu.
        self.env.cr.execute(
            "UPDATE website_menu SET mega_menu_content = %s WHERE id = %s",
            (html_payload, nested_mega.id),
        )

        self.env.invalidate_all()

        return {
            "root": root.id,
            "second": second.id,
            "third": third.id,
            "fourth": fourth.id,
            "mega_child": mega_child.id,
            "nested_mega": nested_mega.id,
        }

    def check(self, init):
        Menu = self.env["website.menu"]

        mega_child = Menu.browse(init["mega_child"])
        self.assertFalse(mega_child.parent_id, "Mega menu children should be promoted to top-level")

        root = Menu.browse(init["root"])
        second = Menu.browse(init["second"])
        third = Menu.browse(init["third"])
        fourth = Menu.browse(init["fourth"])

        self.assertEqual(
            second.parent_id,
            root,
            "Level-one menus should remain attached to their root",
        )
        self.assertEqual(
            third.parent_id,
            root,
            "Level-three menus should be reparented to the top level",
        )
        self.assertEqual(
            fourth.parent_id,
            root,
            "Menus deeper than level two should be flattened under the root",
        )

        nested_mega = Menu.browse(init["nested_mega"])
        self.assertFalse(
            nested_mega.parent_id,
            "Mega menus should not have a parent after migration",
        )
