from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestAiPromptPropertiesMigration(UpgradeCase):
    # Need to be run with CRM for properties
    # > upgradeci retry with crm+ai_fields
    def prepare(self):
        if not util.version_gte("saas~18.4"):
            self.skipTest("This test is only valid from saas~18.4+")

        if "crm.lead" not in self.env:
            # Need CRM to test properties
            self.skipTest("CRM not installed, skip test")

        partner_1, partner_2 = self.env["res.partner"].create(
            [
                {"name": "Partner 1"},
                {"name": "Partner 2"},
            ]
        )

        # `data-ai-field` was not checked, only the value in `t-out`, so for each field,
        # we inject a tag in `data-ai-field`, to verify that we don't keep it after the migration
        prompt = (
            # First fields list inserted
            """<p><t t-out="object._ai_read('active','is_blacklisted','city')" class="o_ai_field" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">"""
            """<span data-ai-field="active__INJECTION_CHECK__">Active</span>"""
            """<br><span data-ai-field="is_blacklisted__INJECTION_CHECK__">Blacklist</span>"""
            """<br><span data-ai-field="city__INJECTION_CHECK__">City</span><br></t></p>"""
            # Insert Qweb whitelisted field
            """<p><span data-oe-protected="true" class="o_ai_field" contenteditable="false"></span></p>"""
            """<div class="d-none o-paragraph">{"display_name":</div><div><t t-out="object.display_name" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">Display Name</t></div><div class="d-none o-paragraph">}</div><p></p>"""
            # Message field inserted
            """<p><t data-ai-field="message_ids__INJECTION_CHECK__" t-out="object.message_ids._ai_format_mail_messages()" class="o_ai_field" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">Messages</t></p>"""
            """<p><span data-oe-protected="true" class="o_ai_field" contenteditable="false"></span></p>"""
            # Relational field inserted
            """<div class="d-none o-paragraph">{"partner_id.name":</div>"""
            """<div><t t-out="object.partner_id.name" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">Customer &gt; Name</t></div>"""
            """<div class="d-none o-paragraph">}</div><p></p>"""
            # Records inserted
            """<div><div class="o_ai_record" data-oe-protected="true" contenteditable="false">"""
            f"""<div class="d-none">{{{partner_1.id}:</div><span>{partner_1.display_name}</span><div class="d-none">}}</div></div> """
            """<div class="o_ai_record" data-oe-protected="true" contenteditable="false">"""
            f"""<div class="d-none">{{{partner_2.id}:</div><span>{partner_2.display_name}</span><div class="d-none">}}</div></div> </div><p><br></p>"""
            # Try to inject field in `data-ai-field`
            """<div t-out="object.test_field"><span data-ai-field="__INJECTION_CHECK__"/></div>"""
            """<t data-ai-field="__INJECTION_CHECK__"/>"""
        )

        team = self.env["crm.team"].create({"name": "team"})
        lead = self.env["crm.lead"].create(
            {
                "name": "Lead",
                "team_id": team.id,
                "lead_properties": [
                    {
                        "ai": True,
                        "ai_domain": [],
                        "comodel": "res.partner",
                        "name": "743a1ba26b746ac2",
                        "string": "Property 1",
                        "system_prompt": prompt,
                        "type": "many2one",
                        "definition_changed": True,
                    },
                ],
            },
        )
        return {
            "lead": lead.id,
            "partner_1": partner_1.id,
            "partner_2": partner_2.id,
        }

    def check(self, init):
        """
        The above example will become:
        <div>
            <span class="o_ai_field" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">
              <span data-ai-field="active" data-oe-protected="true">Active</span>
              <span data-ai-field="is_blacklisted" data-oe-protected="true">Blacklist</span>
              <span data-ai-field="city" data-oe-protected="true">City</span>
            </span>
            <span data-oe-protected="true" class="o_ai_field" contenteditable="false" />
            <span data-oe-t-inline="true" data-oe-protected="true" contenteditable="false" data-ai-field="display_name">Display Name</span>
            <span data-ai-field="message_ids" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">Messages</span>
            <span data-oe-protected="true" class="o_ai_field" contenteditable="false" />
            <span data-oe-t-inline="true" data-oe-protected="true" contenteditable="false" data-ai-field="partner_id.name">Customer &gt; Name</span>
          <div>
            <span data-oe-protected="true" contenteditable="false" data-ai-record-id="6" />
            <span data-oe-protected="true" contenteditable="false" data-ai-record-id="7" />
        </div>
        """
        if not init:
            return

        lead = self.env["crm.lead"].browse(init["lead"])
        partner_1 = self.env["res.partner"].browse(init["partner_1"])
        partner_2 = self.env["res.partner"].browse(init["partner_2"])

        values = lead.read(["lead_properties"])[0]
        prompt = values["lead_properties"][0]["system_prompt"]

        self.assertNotIn("t-out", prompt)
        self.assertNotIn("<t", prompt)
        self.assertNotIn("INJECTION_CHECK", prompt)

        # Check that all fields have been migrated
        self.assertIn('data-ai-field="active"', prompt)
        self.assertIn('data-ai-field="is_blacklisted"', prompt)
        self.assertIn('data-ai-field="city"', prompt)
        self.assertIn('data-ai-field="is_blacklisted"', prompt)
        self.assertIn('data-ai-field="display_name"', prompt)
        self.assertIn('data-ai-field="message_ids"', prompt)
        self.assertIn('data-ai-field="partner_id.name"', prompt)

        # Check that all records inserted have been migrated
        self.assertIn(f'data-ai-record-id="{partner_1.id}"', prompt)
        self.assertIn(f'data-ai-record-id="{partner_2.id}"', prompt)
