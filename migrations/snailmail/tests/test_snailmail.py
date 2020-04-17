# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("13.4")
class TestSnailmailNotification(UpgradeCase):
    def prepare(self):
        dest_partner = self.env["res.partner"].create([{"name": "dest_partner"}])
        letters = self.env["snailmail.letter"].create(
            [
                {"model": dest_partner._name, "res_id": dest_partner.id, "partner_id": dest_partner.id, "state": state}
                for state in ["pending", "sent", "error", "canceled"]
            ]
        )
        return {
            "dest_partner_id": dest_partner.id,
            "letter_ids": letters.ids,
        }

    def check(self, init):
        letters = self.env["snailmail.letter"].browse(init["letter_ids"])
        self.assertEqual(len(letters), 4)
        for letter, notification_status in zip(letters, ["ready", "sent", "exception", "cancelled"]):
            notif = letter.notification_ids
            self.assertEqual(len(notif), 1)
            self.assertEqual(notif.notification_type, "snail")
            self.assertEqual(notif.res_partner_id.id, init["dest_partner_id"])
            self.assertEqual(notif.mail_message_id.id, letter.message_id.id)
            self.assertEqual(notif.notification_status, notification_status)
            self.assertEqual(notif.is_read, True)
