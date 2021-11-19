# -*- coding: utf-8 -*-

from lxml import etree, html

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

utf8_parser = html.HTMLParser(encoding="utf-8")

# `to_class` and `to_style` are the expected results after migration.
# When they are unspecified, the test verifies that the values were not changed.
scenarios = [
    {
        "title": "Old Default",
        "from_class": "s_mega_menu_multi_menus py-4",
        "from_style": "",
        "to_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "to_style": "background-color: white !important;",
    },
    {
        "title": "Default",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc1",
        "from_style": "",
    },
    {
        "title": "CC3",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3",
        "from_style": "",
    },
    {
        "title": "BLACK_25",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level bg-black-25",
        "from_style": "",
        "to_style": "background-color: rgb(191, 191, 191) !important;",
    },
    {
        "title": "CC3+BLACK_25",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3 bg-black-25",
        "from_style": "",
        "to_style": "background-color: rgb(191, 191, 191) !important;",
    },
    {
        "title": "O_COLOR_2",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level bg-o-color-2",
        "from_style": "",
    },
    {
        "title": "CC3+O_COLOR_2",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3 bg-o-color-2",
        "from_style": "",
    },
    {
        "title": "WHITE-50",
        "from_class": "s_mega_menu_multi_menus py-4 bg-white-50",
        "from_style": "",
        "to_style": "background-color: rgb(255, 255, 255) !important;",
        "to_class": "s_mega_menu_multi_menus py-4 bg-white-50 o_colored_level",
    },
    {
        "title": "CC3+WHITE-25",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3 bg-white-25",
        "from_style": "",
        "to_style": "background-color: rgb(255, 255, 255) !important;",
    },
    {
        "title": "SOLID",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "from_style": "background-color: rgb(254, 93, 93) !important;",
    },
    {
        "title": "CC3+SOLID",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3",
        "from_style": "background-color: rgb(254, 93, 93) !important;",
    },
    {
        "title": "TRANSPARENT",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "from_style": "background-color: rgba(254, 93, 93, 0.5) !important;",
        "to_style": "background-color: rgb(254, 174, 174) !important;",
    },
    {
        "title": "TRANSPARENT+BG_IMAGE",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "from_style": "background-color: rgba(254, 93, 93, 0.5) !important; background-image: url(XXX);",
        "to_style": "background-color: rgb(254, 174, 174) !important; background-image: url(XXX);",
    },
    {
        "title": "CC3+TRANSPARENT",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3",
        "from_style": "background-color: rgba(254, 93, 93, 0.5) !important;",
        "to_style": "background-color: rgb(254, 174, 174) !important;",
    },
    {
        "title": "GRADIENT",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "from_style": "background-color: rgba(0, 0, 0, 0) !important; background-image: "
        "linear-gradient(135deg, rgb(255, 204, 51) 0%, rgb(226, 51, 255) 100%) !important;",
    },
    {
        "title": "CC3+GRADIENT",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level o_cc o_cc3",
        "from_style": "background-color: rgba(0, 0, 0, 0) !important; background-image: "
        "linear-gradient(135deg, rgb(255, 204, 51) 0%, rgb(226, 51, 255) 100%) !important;",
    },
    {
        "title": "TRANSPARENT LINEAR GRADIENT",
        "from_class": "s_mega_menu_multi_menus py-4",
        "from_style": "background-color: rgba(0, 0, 0, 0) !important; background-image: "
        "linear-gradient(135deg, rgb(255, 204, 51) 0%, rgba(226, 51, 255, 0.27) 100%);",
        "to_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "to_style": "background-color: rgba(0, 0, 0, 0) !important; background-image: "
        "linear-gradient(135deg, rgb(255, 204, 51) 0%, rgb(247, 199, 255) 100%);",
    },
    {
        "title": "TRANSPARENT RADIAL GRADIENT + IMAGE",
        "from_class": "s_mega_menu_multi_menus py-4 o_colored_level",
        "from_style": "background-color: rgba(0, 0, 0, 0) !important; background-image: "
        'url("/web_editor/shape/illustration/fishing-svg-2056?c1=%2335979C&unique=98d68d58"),'
        "radial-gradient(circle farthest-side at 25% 25%, "
        "rgba(255, 204, 51, 0.99) 0%, rgba(226, 51, 255, 0.36) 100%) !important;",
        "to_style": "background-color: rgba(0, 0, 0, 0) !important; background-image: "
        'url("/web_editor/shape/illustration/fishing-svg-2056?c1=%2335979C&unique=98d68d58"),'
        "radial-gradient(circle farthest-side at 25% 25%, rgb(255, 204, 53) 0%, rgb(244, 181, 255) 100%) !important;",
    },
    {
        "title": "MULTI TRANSPARENT LINEAR GRADIENT + IMAGE",
        "from_class": "s_mega_menu_multi_menus py-4",
        "from_style": "background-image: url(https://11049240-15-0-all.runbot61.odoo.com/web_editor/shape/"
        "illustration/fishing-svg-2427?c1=%23DE6528unique=98d68d58), linear-gradient(135deg, "
        "rgba(255, 204, 51, 0.2) 0%, rgba(244, 159, 99, 0.88) 25%, rgba(233, 117, 143, 0.64) 48%, rgba(221, 69,"
        " 194, 0.79) 75%, rgba(210, 24, 242, 0) 100%) !important; background-color: rgba(0, 0, 0, 0) !important;",
        "to_style": "background-image: url(https://11049240-15-0-all.runbot61.odoo.com/web_editor/shape/"
        "illustration/fishing-svg-2427?c1=%23DE6528unique=98d68d58), linear-gradient(135deg, "
        "rgb(255, 244, 214) 0%, rgb(245, 170, 117) 25%, rgb(240, 166, 183) 48%, rgb(228, 108, 206)"
        " 75%, rgb(255, 255, 255) 100%) !important; background-color: rgba(0, 0, 0, 0) !important;",
        "to_class": "s_mega_menu_multi_menus py-4 o_colored_level",
    },
]


@change_version("saas~15.2")
class TestMegaMenu(UpgradeCase):
    def prepare(self):
        menu_specs = [
            {
                "name": "Mega Menu Test (%s)" % scenario.get("title"),
                "website_id": self.env.ref("website.default_website").id,
                "is_mega_menu": True,
            }
            for scenario in scenarios
        ]
        menu_ids = self.env["website.menu"].create(menu_specs)
        for scenario, menu_id in zip(scenarios, menu_ids):
            content = html.fromstring(menu_id.mega_menu_content, parser=utf8_parser)
            content.set("class", scenario.get("from_class"))
            content.set("style", scenario.get("from_style"))
            menu_id.write(
                {
                    "mega_menu_content": etree.tostring(content, encoding="unicode"),
                }
            )
        return {"menu_ids": menu_ids.ids}

    def check(self, init):
        for scenario, menu in zip(scenarios, self.env["website.menu"].browse(init["menu_ids"])):
            content = html.fromstring(menu.mega_menu_content, parser=utf8_parser)
            self.assertEqual(
                content.get("class"),
                scenario.get("to_class", scenario.get("from_class", "")),
                "Class of %s" % scenario.get("title"),
            )
            self.assertEqual(
                content.get("style", ""),
                scenario.get("to_style", scenario.get("from_style", "")),
                "Style of %s" % scenario.get("title"),
            )
