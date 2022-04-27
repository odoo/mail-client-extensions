from odoo.addons.base.maintenance.migrations.testing import UpgradeCase


class TestEnFrancais(UpgradeCase):
    """Install the french lang in order to coverage the queries on ir_translation"""

    def prepare(self):
        Lang = self.env["res.lang"]
        if hasattr(Lang, "_activate_lang"):
            Lang._activate_lang("fr_FR")
        else:
            Lang.load_lang("fr_FR")

        Mod = self.env["ir.module.module"]
        Mod.browse(Mod._installed().values())._update_translations(["fr_FR"])

    def check(self, _):
        installed = self.env["res.lang"].get_installed()
        self.assertIn("fr_FR", dict(installed))
