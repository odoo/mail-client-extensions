from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.4")
class TestVoipConfigMoved(UpgradeCase):
    test_voip_config = {
        "mobile_call_method": "voip",
        "sip_always_transfer": True,
        "sip_external_phone": "+353209126911",
        "sip_ignore_incoming": True,
        "sip_login": "1337",
        "sip_password": "123456",
    }

    def prepare(self):
        # There are two cases to be tested: users with a pre-existing relation
        # to res.users.settings, and users without.
        user1 = self.env["res.users"].create(
            {
                "login": "vive_minecraft",
                "name": "Grandgousier",
                **self.test_voip_config,
            }
        )
        # Add a relation to res.users.settings (testing the query for users with
        # a pre-existing relation to res.users.settings):
        self.env["res.users.settings"].create({"user_id": user1.id})
        user2 = self.env["res.users"].create(
            {
                "login": "roblox_gaming",
                "name": "Gargamelle",
                **self.test_voip_config,
            }
        )
        return {"user_ids": [user1.id, user2.id]}

    def check(self, init):
        user1, user2 = self.env["res.users"].browse(init["user_ids"])
        self._check_values_have_been_moved(user1, user2)

    def _check_values_have_been_moved(self, user1, user2):
        rename_table = [
            ("mobile_call_method", "how_to_call_on_mobile"),
            ("sip_always_transfer", "should_call_from_another_device"),
            ("sip_external_phone", "external_device_number"),
            ("sip_ignore_incoming", "should_auto_reject_incoming_calls"),
            ("sip_login", "voip_username"),
            ("sip_password", "voip_secret"),
        ]
        for old_name, new_name in rename_table:
            # Note: the fields we want to check have a 'related' on res.users.
            self.assertEqual(self.test_voip_config.get(old_name), user1[new_name])
            self.assertEqual(self.test_voip_config.get(old_name), user2[new_name])
