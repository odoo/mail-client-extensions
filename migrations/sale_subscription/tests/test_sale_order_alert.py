# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class Test_00_Simple_SaleOrderAlert_BaseAutomation_Upgrade(UpgradeCase):
    def prepare(self):
        alert = self.env["sale.order.alert"].create(
            {
                "name": "Take action on less satisfied clients",
                "model_id": self.env.ref("sale.model_sale_order").id,
                "rating_operator": "<",
                "rating_percentage": 30,
                "trigger_condition": "on_time",
                "trg_date_id": self.env["ir.model.fields"]
                .search([("model", "=", "sale.order"), ("name", "=", "start_date")])
                .id,
                "trg_date_range": 1,
                "trg_date_range_type": "month",
                "action": "next_activity",
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "activity_date_deadline_range": 5,
                "activity_user": "contract",
                "activity_note": "Please call the client to get some feedback about its subscription.",
            }
        )
        alert.write({"activity_type_id": self.env.ref("mail.mail_activity_data_todo").id})
        return {
            "alert_id": alert.id,
            "automation_id": alert.automation_id.id,
        }

    def check(self, check):
        alert = self.env["sale.order.alert"].browse(check["alert_id"])
        automation = self.env["base.automation"].browse(check["automation_id"])
        self.assertEqual(len(automation.action_server_ids), 1)
        action = automation.action_server_ids[0]
        self.assertRecordValues(
            automation,
            [
                {
                    "active": True,
                    "name": "Take action on less satisfied clients",
                    "model_id": self.env.ref("sale.model_sale_order").id,
                    "trigger": "on_time",
                    "filter_pre_domain": "[]",
                    "filter_domain": "[('is_subscription', '=', True), ('percentage_satisfaction', '<', 30)]",
                    "is_sale_order_alert": True,
                    "trg_date_id": self.env["ir.model.fields"]
                    .search([("model", "=", "sale.order"), ("name", "=", "start_date")])
                    .id,
                    "trg_date_range": 1,
                    "trg_date_range_type": "month",
                    "action_server_ids": [action.id],
                }
            ],
        )
        self.assertRecordValues(
            alert,
            [
                {
                    "active": True,
                    "automation_id": automation.id,
                    "action_id": action.id,
                    "activity_user": "contract",
                    "activity_note": Markup(
                        "<p>Please call the client to get some feedback about its subscription.</p>"
                    ),
                    "activity_date_deadline_range": 5,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                }
            ],
        )
        self.assertRecordValues(
            action,
            [
                {
                    "name": "Take action on less satisfied clients",
                    "state": "next_activity",
                    "activity_user_type": "generic",
                    "activity_user_field_name": "user_id",
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "activity_date_deadline_range": 5,
                    "activity_note": Markup(
                        "<p>Please call the client to get some feedback about its subscription.</p>"
                    ),
                }
            ],
        )
