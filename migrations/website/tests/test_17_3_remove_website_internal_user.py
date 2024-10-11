try:
    from odoo import Command
except ImportError:
    # old odoo version, ignore the error as the test only runs for saas~17.3 changes
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestWebsiteModel(UpgradeCase):
    def prepare(self):
        website2 = self.env["website"].create(
            {
                "name": "My Website 2",
                "domain": "",
                "sequence": 20,
            }
        )
        # internal user with website reference. need to set null website reference.
        internal_user = self.env["res.users"].create(
            {
                "name": "Internal User with website not null",
                "login": "user_website_1",
                "website_id": self.env.ref("website.default_website").id,
            }
        )
        # portal user with website_id reference. so need to set null reference.
        portal_group = self.env.ref("base.group_portal")
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal User",
                "login": "portal_user",
                "website_id": website2.id,
                "groups_id": [Command.set([portal_group.id])],
            }
        )
        return {"internal_user": internal_user.ids, "portal_user": portal_user.ids}

    def check(self, init):
        internal_user = self.env["res.users"].browse(init["internal_user"])
        self.assertFalse(internal_user.website_id, "Remove website on related partner before they become internal user")
        portal_user = self.env["res.users"].browse(init["portal_user"])
        self.assertTrue(portal_user.website_id)
