# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("13.4")
class TestSnailmailNotification(UpgradeCase):
    def prepare(self):
        dest_partner = self.env["res.partner"].create([{"name": "dest_partner"}])
        letters = self.env["snailmail.letter"].create(
            [
                {
                    "model": dest_partner._name,
                    "res_id": dest_partner.id,
                    "partner_id": dest_partner.id,
                    "state": state,
                    "error_code": "NO_PRICE_AVAILABLE" if state == "error" else False,
                    "info_msg": "more info about %s" % state,
                }
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
            if notif.notification_status != "exception":
                self.assertFalse(notif.failure_type)
                self.assertFalse(notif.failure_reason)
            else:
                self.assertEqual(notif.failure_type, "sn_price")
                self.assertEqual(notif.failure_reason, "more info about error")


@change_version("13.4")
class TestSnailmailNotificationError(UpgradeCase):
    def prepare(self):
        dest_partner = self.env["res.partner"].create([{"name": "dest_partner"}])
        letters = self.env["snailmail.letter"].create(
            [
                {
                    "model": dest_partner._name,
                    "res_id": dest_partner.id,
                    "partner_id": dest_partner.id,
                    "state": "error",
                    "error_code": error_code,
                    "info_msg": "more info about error",
                }
                for error_code in [
                    "CREDIT_ERROR",
                    "TRIAL_ERROR",
                    "NO_PRICE_AVAILABLE",
                    "MISSING_REQUIRED_FIELDS",
                    "FORMAT_ERROR",
                    "UNKNOWN_ERROR",
                ]
            ]
        )
        return {
            "dest_partner_id": dest_partner.id,
            "letter_ids": letters.ids,
        }

    def check(self, init):
        letters = self.env["snailmail.letter"].browse(init["letter_ids"])
        self.assertEqual(len(letters), 6)
        for letter, failure_type in zip(
            letters, ["sn_credit", "sn_trial", "sn_price", "sn_fields", "sn_format", "sn_error"]
        ):
            notif = letter.notification_ids
            self.assertEqual(len(notif), 1)
            self.assertEqual(notif.notification_status, "exception")
            self.assertEqual(notif.failure_type, failure_type)
            self.assertEqual(notif.failure_reason, "more info about error")
