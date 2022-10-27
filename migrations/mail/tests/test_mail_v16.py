from odoo.tests import tagged

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@tagged("mail_v16")
@change_version("saas~16.1")
class TestMailNotificationTypeGroup(UpgradeCase):
    def prepare(self):
        user = self.env["res.users"].create(
            {
                "name": "foo",
                "login": "TestMailNotificationTypeGroup",
                "notification_type": "inbox",
            }
        )
        return {"user_id": user.id}

    def check(self, init):
        user = self.env["res.users"].browse(init["user_id"])
        self.assertTrue(
            user.has_group("mail.group_mail_notification_type_inbox"),
            "A user with the inbox notification type must have the group `mail.group_mail_notification_type_inbox`",
        )
