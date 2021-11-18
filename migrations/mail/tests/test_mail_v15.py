# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io

from PIL import Image

from odoo.tests import tagged

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@tagged("mail_v15")
@change_version("saas~14.5")
class TestMailChannel(UpgradeCase):
    def prepare(self):
        MailChannel = self.env["mail.channel"]
        MailAlias = self.env["mail.alias"]
        User = self.env["res.users"].with_context(no_reset_password=True)
        Partner = self.env["res.partner"]
        Moderation = self.env["mail.moderation"]

        user_1, user_2, user_3 = User.create(
            [
                {
                    "name": "User %i" % i,
                    "login": "user_%i@example.com" % i,
                    "email": '"User" <user_%i@EXAMPLE.com>' % i,
                    "groups_id": self.env.ref("base.group_user").ids,
                    "company_ids": self.env.company.ids,
                    "company_id": self.env.company.id,
                }
                for i in range(3)
            ]
        )

        partner = Partner.create(
            {
                "name": "Test partner",
                "email": '"Partner" <partner@example.com>',
            }
        )

        # Standard <mail.channel>
        channel_1 = MailChannel.create(
            {
                "name": "Channel 1",
                "email_send": False,
                "channel_partner_ids": [
                    (4, user_1.partner_id.id),
                    (4, user_2.partner_id.id),
                    (4, user_3.partner_id.id),
                    (4, partner.id),
                ],
                "image_128": self._create_b64_image("#FF0000"),
                "public": "public",
            }
        )

        for _ in range(4):
            self._create_message(channel_1, email=False)
        for _ in range(5):
            self._create_message(channel_1, email=True)

        # Email <mail.channel> not moderated
        channel_2 = MailChannel.create(
            {
                "name": "Channel 2",
                "email_send": True,
                "moderation": False,
                "channel_partner_ids": [(4, user_1.partner_id.id)],
                "image_128": self._create_b64_image("#00FF00"),
                "public": "private",
                "alias_contact": "followers",
            }
        )
        self.assertEqual(channel_2.alias_id.alias_contact, "followers")

        for _ in range(2):
            self._create_message(channel_2, email=True)

        # Email <mail.channel> moderated
        channel_3 = MailChannel.create(
            {
                "name": "Channel 3",
                "email_send": True,
                "moderation": True,
                "moderator_ids": user_1 | user_2,
                "channel_partner_ids": [
                    (4, user_1.partner_id.id),
                    (4, user_2.partner_id.id),
                    (4, partner.id),
                ],
                "description": "Description of the channel.\nLine 2.",
                "moderation_ids": [],
                "moderation_notify": True,
                "moderation_notify_msg": "Your message is pending moderation",
                "moderation_guidelines": True,
                "moderation_guidelines_msg": "Be nice, it's not nice to be bad",
                "alias_name": "channel_3",
                "image_128": self._create_b64_image("#0000FF"),
                "public": "groups",
                "alias_contact": "followers",
                "group_public_id": self.env.ref("base.group_partner_manager").id,
            }
        )

        message_1 = self._create_message(
            channel_3, email=True, subject="M1", moderation_status="accepted", moderator_id=user_2.id
        )
        self._create_message(channel_3, email=True, subject="M2", moderation_status="rejected", moderator_id=user_3.id)
        self._create_message(channel_3, email=True, subject="M3", moderation_status="pending_moderation")
        child_1 = self._create_message(
            channel_3, email=True, subject="M1 - 1", moderation_status="pending_moderation", parent_id=message_1.id
        )
        self._create_message(
            channel_3, email=True, subject="M1 - 2", moderation_status="rejected", parent_id=message_1.id
        )
        self._create_message(
            channel_3, email=True, subject="M1 - 1 - 1", moderation_status="accepted", parent_id=child_1.id
        )

        # Create the moderation rules
        Moderation.create(
            [
                {
                    "email": "alice@example.com",
                    "status": "allow",
                    "channel_id": channel_2.id,
                },
                {
                    "email": '"Bob" <bob@example.com>',
                    "status": "ban",
                    "channel_id": channel_3.id,
                },
                {
                    "email": '"Anne" <anne@exAMple.cOM>',
                    "status": "ban",
                    "channel_id": channel_3.id,
                },
            ]
        )

        # Should not touch this alias
        alias = MailAlias.create(
            {
                "alias_name": "random_alias",
                "alias_model_id": self.env["ir.model"]._get("mail.channel").id,
                "alias_force_thread_id": channel_1.id,
                "alias_contact": "partners",
            }
        )

        # Sanity check: mail alias
        self.assertEqual(channel_2.alias_id.alias_model_id.model, "mail.channel")
        self.assertEqual(channel_2.alias_id.alias_force_thread_id, channel_2.id)
        self.assertEqual(channel_2.alias_id.alias_defaults, "{}")
        self.assertEqual(channel_3.alias_id.alias_model_id.model, "mail.channel")
        self.assertEqual(channel_3.alias_id.alias_force_thread_id, channel_3.id)

        # Sanity check: channel images
        images = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "mail.channel"),
                ("res_id", "in", [channel_1.id, channel_2.id, channel_3.id]),
                ("res_field", "=", "image_128"),
            ],
        )
        self.assertEqual(len(images), 3)

        # Sanity check: mail channel
        self.assertEqual(len(channel_1.channel_partner_ids), 4)
        self.assertEqual(len(channel_2.channel_partner_ids), 1)
        self.assertEqual(len(channel_3.channel_partner_ids), 3)

        return {
            "channel_1": channel_1.id,
            "channel_2": channel_2.id,
            "channel_3": channel_3.id,
            "alias": alias.id,
            "user_1": user_1.id,
            "user_2": user_2.id,
            "user_3": user_3.id,
            "partner": partner.id,
        }

    def check(self, init):
        MailChannel = self.env["mail.channel"]
        MailAlias = self.env["mail.alias"]
        User = self.env["res.users"].with_context(no_reset_password=True)
        Partner = self.env["res.partner"]
        User = self.env["res.users"]
        Group = self.env["mail.group"]
        Member = self.env["mail.group.member"]
        Moderation = self.env["mail.group.moderation"]
        Message = self.env["mail.group.message"]

        channel_1 = MailChannel.browse(init["channel_1"]).exists()
        channel_2 = MailChannel.browse(init["channel_2"]).exists()
        channel_3 = MailChannel.browse(init["channel_3"]).exists()

        user_1 = User.browse(init["user_1"]).exists()
        user_2 = User.browse(init["user_2"]).exists()
        partner = Partner.browse(init["partner"]).exists()

        self.assertTrue(channel_1, "Should have kept standard mail channel")
        self.assertFalse(channel_2, "Should have removed email mail channel")
        self.assertFalse(channel_3, "Should have removed email mail channel")

        group_1 = Group.search([("name", "=", "Channel 1")])
        group_2 = Group.search([("name", "=", "Channel 2")])
        group_3 = Group.search([("name", "=", "Channel 3")])

        self.assertFalse(group_1, "Should not have created a group for standard channel")
        self.assertTrue(group_2, "Should have created a group for email channel")
        self.assertTrue(group_3, "Should have created a group for email channel")
        self.assertEqual(channel_1.public, "public")
        self.assertEqual(group_2.access_mode, "members", "Should have changed the old privacy 'private' to 'members'")
        self.assertEqual(group_3.access_mode, "groups")
        self.assertEqual(
            group_3.access_group_id, self.env.ref("base.group_partner_manager"), "Should not have changed the group"
        )
        self.assertEqual(group_3.moderator_ids, user_1 | user_2, "Should have moved the moderators")
        self.assertEqual(group_3.moderation, True)
        self.assertEqual(group_3.description, "Description of the channel.\nLine 2.")
        self.assertEqual(group_3.moderation_notify, True)
        self.assertEqual(group_3.moderation_notify_msg, "<p>Your message is pending moderation</p>")
        self.assertEqual(group_3.moderation_guidelines, True)
        self.assertEqual(group_3.moderation_guidelines_msg, "<p>Be nice, it's not nice to be bad</p>")
        self.assertEqual(group_3.alias_name, "channel_3")

        # Check the image field on the group / channel
        self.assertEqual(
            channel_1.image_128,
            self._create_b64_image("#FF0000"),
            "Should not have changed the image of the mail channel",
        )
        self.assertEqual(
            group_2.image_128,
            self._create_b64_image("#00FF00"),
            "Should have moved the image of the mail group",
        )
        self.assertEqual(
            group_3.image_128,
            self._create_b64_image("#0000FF"),
            "Should have moved the image of the mail group",
        )

        # Check the mail alias
        alias = MailAlias.browse(init["alias"]).exists()
        self.assertEqual(alias.alias_name, "random_alias", "Should not have touched non-pertinent alias")
        self.assertEqual(alias.alias_model_id.model, "mail.channel", "Should not have touched non-pertinent alias")
        self.assertEqual(alias.alias_force_thread_id, channel_1.id, "Should not have touched non-pertinent alias")
        self.assertEqual(alias.alias_contact, "partners", "Should not have touched non-pertinent alias")

        self.assertTrue(group_2.alias_id)
        self.assertEqual(group_2.alias_id.alias_model_id.model, "mail.group", "Should have updated the alias")
        self.assertEqual(group_2.alias_id.alias_force_thread_id, group_2.id, "Should have updated the alias")
        self.assertEqual(group_2.alias_id.alias_contact, "followers")

        self.assertTrue(group_3.alias_id)
        self.assertEqual(group_3.alias_id.alias_name, "channel_3", "Should keep the alias name")
        self.assertEqual(group_3.alias_id.alias_model_id.model, "mail.group", "Should have updated the alias")
        self.assertEqual(group_3.alias_id.alias_force_thread_id, group_3.id, "Should have updated the alias")
        self.assertEqual(group_3.alias_id.alias_contact, "followers")

        # Check that members were added
        self.assertEqual(len(channel_1.channel_partner_ids), 4, "Should not have touched non-email mail channel")
        self.assertEqual(len(group_2.member_ids), 1, "Should have created members")
        self.assertEqual(len(group_3.member_ids), 3, "Should have created members")
        self.assertTrue(
            Member.search(
                [
                    ("mail_group_id", "=", group_2.id),
                    ("email", "=", '"User" <user_0@EXAMPLE.com>'),
                    ("email_normalized", "=", "user_0@example.com"),
                ]
            )
        )
        self.assertTrue(
            Member.search(
                [
                    ("mail_group_id", "=", group_2.id),
                    ("email", "=", '"User" <user_0@EXAMPLE.com>'),
                    ("email_normalized", "=", "user_0@example.com"),
                    ("partner_id", "=", user_1.partner_id.id),
                ]
            )
        )
        self.assertTrue(
            Member.search(
                [
                    ("mail_group_id", "=", group_3.id),
                    ("email", "=", '"Partner" <partner@example.com>'),
                    ("email_normalized", "=", "partner@example.com"),
                    ("partner_id", "=", partner.id),
                ]
            )
        )

        # Check the moderation rules
        self.assertEqual(len(group_2.moderation_rule_ids), 1, "Should have moved the moderation rules")
        self.assertEqual(len(group_3.moderation_rule_ids), 2, "Should have moved the moderation rules")
        self.assertTrue(
            Moderation.search(
                [
                    ("mail_group_id", "=", group_3.id),
                    ("email", "=", "anne@example.com"),
                    ("status", "=", "ban"),
                ]
            )
        )

        # Check the message
        self.assertEqual(len(group_2.mail_group_message_ids), 2)
        self.assertEqual(len(group_3.mail_group_message_ids), 6)

        message_child = Message.search([("subject", "=", "M1 - 1 - 1")])
        self.assertTrue(message_child)
        self.assertEqual(message_child.moderation_status, "accepted")
        self.assertEqual(
            message_child.group_message_parent_id.subject,
            "M1 - 1",
            "Should have set the group message parent of the message",
        )
        self.assertEqual(
            message_child.group_message_parent_id.group_message_parent_id.subject,
            "M1",
            "Should have set the group message parent of the message",
        )

        last_mail_group_id = max(self.env["mail.group"].search([]).ids)
        new_group = self.env["mail.group"].create({"name": "New group"})
        self.assertEqual(
            new_group.id, last_mail_group_id + 1, "Should have updated the sequence of the mail_group table"
        )

    def _create_message(self, channel, email=True, **kwargs):
        return self.env["mail.message"].create(
            {
                "model": "mail.channel",
                "res_id": channel.id,
                "message_type": "email" if email else "comment",
                **kwargs,
            }
        )

    def _create_b64_image(self, color="#FFFFFF"):
        f = io.BytesIO()
        Image.new("RGB", (40, 40), color).save(f, "PNG")
        f.seek(0)
        return base64.b64encode(f.read())
