# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class SmsOutgoingAddTrackers(UpgradeCase):
    def prepare(self):
        numbers = (("10", "outgoing"), ("20", "error"), ("30", "canceled"), ("40", "outgoing"))
        new_sms = (
            self.env["sms.sms"]
            .sudo()
            .create(
                [
                    {"body": f"body {idx}", "number": number, "state": state}
                    for idx, (number, state) in enumerate(numbers)
                ]
            )
        )
        return {"sms_ids": new_sms.ids}

    def check(self, init):
        new_sms = self.env["sms.sms"].browse(init["sms_ids"])
        outgoing_sms = new_sms.filtered(lambda s: s.state == "outgoing")
        sms_with_uuid = new_sms.filtered("uuid")
        self.assertEqual(outgoing_sms, sms_with_uuid)
