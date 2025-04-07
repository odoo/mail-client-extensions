try:
    from odoo import Command, fields
except ImportError:
    # `Command` is only available in recent versions
    Command = fields = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestPartnershipUpgrade(UpgradeCase):
    @property
    def key(self):
        return "membership.tests.test_membership_partnership_18_3.TestPartnershipUpgrade"

    def prepare(self):
        # The prepare is defined in membership/tests/test_membership_partnership_18_3.py
        return []

    def check(self, init):
        membership = self.env["product.product"].browse(init["membership"])
        self.assertEqual(membership.service_tracking, "partnership")
        self.assertEqual(membership.type, "service")
        self.assertEqual(membership.grade_id.name, membership.name)
        self.assertTrue(membership.active)
        self.assertTrue(membership.grade_id.active)

        old_membership = self.env["product.product"].browse(init["old_membership"])
        self.assertEqual(old_membership.service_tracking, "partnership")
        self.assertEqual(old_membership.type, "service")
        self.assertEqual(old_membership.grade_id.name, old_membership.name)
        self.assertFalse(old_membership.active)
        self.assertFalse(old_membership.grade_id.active)

        partner1 = self.env["res.partner"].browse(init["partner1"])
        self.assertEqual(partner1.grade_id, membership.grade_id)
        self.assertIn("Membership history", partner1.message_ids[0].body)

        partner2 = self.env["res.partner"].browse(init["partner2"])
        self.assertFalse(partner2.grade_id)
        self.assertIn("Membership history", partner2.message_ids[0].body)

        partner3 = self.env["res.partner"].browse(init["partner3"])
        self.assertFalse(partner3.grade_id)
        self.assertNotIn("Membership history", partner3.message_ids[0].body)
