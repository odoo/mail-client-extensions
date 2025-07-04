import ast
import re

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.1")
class TestMigrateHelpdeskTicketTypeInHelpdeskTag(UpgradeCase):
    def prepare(self):
        ticket_type_1, ticket_type_2, ticket_type_3, ticket_type_4 = self.env["helpdesk.ticket.type"].create(
            [
                {"name": "UPG:saas~17.1 helpdesk ticket type 1"},
                {"name": "UPG:saas~17.1 helpdesk ticket type 2"},
                {"name": "UPG:saas~17.1 helpdesk ticket type 3"},
                {"name": "UPG:saas~17.1 helpdesk tag 3"},
            ]
        )
        team_1 = self.env["helpdesk.team"].create({"name": "Helpdesk Team 1"})
        tag_1, tag_2, tag_3 = self.env["helpdesk.tag"].create(
            [
                {"name": "helpdesk tag 1"},
                {"name": "helpdesk tag 2"},
                {"name": "UPG:saas~17.1 helpdesk tag 3"},
            ]
        )
        tickets = (
            self.env["helpdesk.ticket"]
            .with_context(default_team_id=team_1.id)
            .create(
                [
                    {"name": "helpdesk ticket 1", "tag_ids": [tag_1.id, tag_2.id], "ticket_type_id": ticket_type_1.id},
                    {"name": "helpdesk ticket 2", "tag_ids": tag_1.ids, "ticket_type_id": ticket_type_1.id},
                    {"name": "helpdesk ticket 3", "ticket_type_id": ticket_type_2.id},
                    {"name": "helpdesk ticket 4", "tag_ids": [tag_1.id, tag_2.id]},
                    {"name": "helpdesk ticket 5", "tag_ids": tag_1.ids},
                    {"name": "helpdesk ticket 6"},
                    {"name": "helpdesk ticket 7", "ticket_type_id": ticket_type_4.id},
                    {"name": "helpdesk ticket 8", "tag_ids": tag_3.ids},
                ]
            )
        )

        slas = self.env["helpdesk.sla"].create(
            [
                {
                    "name": "SLA 1",
                    "team_id": team_1.id,
                    "time": 1,
                    "priority": "1",
                    "ticket_type_ids": ticket_type_1.ids,
                },
                {
                    "name": "SLA 2",
                    "team_id": team_1.id,
                    "time": 1,
                    "priority": "1",
                    "tag_ids": tag_1.ids,
                    "ticket_type_ids": ticket_type_1.ids,
                },
                {
                    "name": "SLA 3",
                    "team_id": team_1.id,
                    "time": 1,
                    "priority": "1",
                    "tag_ids": tag_3.ids,
                    "ticket_type_ids": ticket_type_4.ids,
                },
                {"name": "SLA 4", "team_id": team_1.id, "time": 1, "priority": "1", "tag_ids": tag_2.ids},
            ]
        )

        ticket_types = ticket_type_1 + ticket_type_2 + ticket_type_3 + ticket_type_4
        tags = tag_1 + tag_2 + tag_3

        # create a view to check the filters are correctly adapted
        search_views = self.env["ir.ui.view"].create(
            [
                {
                    "name": "helpdesk.ticket.search",
                    "type": "search",
                    "model": "helpdesk.ticket",
                    "arch": f"""
                    <search>
                        <filter name="ticket_type" domain="[('ticket_type_id', '=', False)]" string="Ticket Type"/>
                        <filter name="ticket_type_1" domain="[('ticket_type_id', '=', {ticket_type_1.id})]" string="Ticket Type 1"/>
                        <filter name="ticket_type_2" domain="[('ticket_type_id', 'in', {ticket_types.ids})]" string="Ticket Type 2"/>
                        <filter name="ticket_type_3" domain="[('ticket_type_id', 'ilike', 'UPG:saas~17.1 %')]" string="Ticket Type 3"/>
                        <filter name="ticket_type_4" domain="[('ticket_type_id', '=', {ticket_type_4.id})]" string="Ticket Type 4"/>
                        <filter name="ticket_type_5" domain="[('ticket_type_id', '=', 999)]" string="Ticket Type 5"/>
                    </search>
                """,
                },
                {
                    "name": "helpdesk.sla.search",
                    "type": "search",
                    "model": "helpdesk.sla",
                    "arch": f"""
                    <search>
                        <filter name="ticket_type" domain="[('ticket_type_ids', '=', False)]" string="Ticket Type"/>
                        <filter name="ticket_type_1" domain="[('ticket_type_ids', 'in', {ticket_type_1.ids})]" string="Ticket Type 1"/>
                        <filter name="ticket_type_2" domain="[('ticket_type_ids', 'in', {ticket_types.ids})]" string="Ticket Type 2"/>
                        <filter name="ticket_type_3" domain="[('ticket_type_ids', 'ilike', 'UPG:saas~17.1 %')]" string="Ticket Type 3"/>
                        <filter name="ticket_type_4" domain="[('ticket_type_ids', 'in', {ticket_type_4.ids})]" string="Ticket Type 4"/>
                        <filter name="ticket_type_5" domain="[('ticket_type_ids.name', 'ilike', 'UPG:saas~17.1 %')]" string="Ticket Type 5"/>
                        <filter name="ticket_type_6" domain="[('ticket_type_ids', '=', {ticket_type_1.id})]" string="Ticket Type 1 (with = operator)"/>
                        <filter name="ticket_type_7" domain="[('ticket_type_ids', 'in', [999])]" string="Ticket Type 6"/>
                    </search>
                """,
                },
            ]
        )
        return (
            ticket_types.ids,
            tags.ids,
            tickets.ids,
            slas.ids,
            search_views.ids,
        )

    def check(self, init):
        ticket_type_ids, tag_ids, ticket_ids, sla_ids, search_view_ids = init

        ticket_1, ticket_2, ticket_3, ticket_4, ticket_5, ticket_6, ticket_7, ticket_8 = self.env[
            "helpdesk.ticket"
        ].browse(ticket_ids)
        tag_1, tag_2, tag_3 = self.env["helpdesk.tag"].browse(tag_ids)
        ticket_type_tags = self.env["helpdesk.tag"].search([("name", "like", "UPG:saas~17.1 %")])
        sla_1, sla_2, sla_3, sla_4 = self.env["helpdesk.sla"].browse(sla_ids)
        ticket_search_view, sla_search_view = self.env["ir.ui.view"].browse(search_view_ids)

        self.assertEqual(len(ticket_type_ids), 4, "all helpdesk ticket type should be migrate except the last one.")
        ticket_type_tag_names = ticket_type_tags.mapped("name")
        self.assertIn("UPG:saas~17.1 helpdesk ticket type 1", ticket_type_tag_names)
        self.assertIn("UPG:saas~17.1 helpdesk ticket type 2", ticket_type_tag_names)
        self.assertIn("UPG:saas~17.1 helpdesk ticket type 3", ticket_type_tag_names)
        self.assertIn("UPG:saas~17.1 helpdesk tag 3", ticket_type_tag_names)

        self.assertEqual(len(ticket_1.tag_ids), 3)
        self.assertIn(tag_1, ticket_1.tag_ids)
        self.assertIn(tag_2, ticket_1.tag_ids)
        helpdesk_ticket_type1_tag = ticket_1.tag_ids - tag_1 - tag_2
        self.assertEqual(helpdesk_ticket_type1_tag.name, "UPG:saas~17.1 helpdesk ticket type 1")

        self.assertEqual(len(ticket_2.tag_ids), 2)
        self.assertIn(tag_1, ticket_2.tag_ids)
        self.assertEqual(helpdesk_ticket_type1_tag.name, "UPG:saas~17.1 helpdesk ticket type 1")

        self.assertEqual(len(ticket_3.tag_ids), 1)
        self.assertEqual(ticket_3.tag_ids.name, "UPG:saas~17.1 helpdesk ticket type 2")

        self.assertEqual(len(ticket_4.tag_ids), 2)
        self.assertIn(tag_1, ticket_4.tag_ids)
        self.assertIn(tag_2, ticket_4.tag_ids)

        self.assertEqual(len(ticket_5.tag_ids), 1)
        self.assertIn(tag_1, ticket_5.tag_ids)

        self.assertFalse(ticket_6.tag_ids)

        self.assertEqual(len(ticket_7.tag_ids), 1)
        self.assertEqual(ticket_7.tag_ids, tag_3)

        self.assertEqual(len(ticket_8.tag_ids), 1)
        self.assertEqual(ticket_8.tag_ids, tag_3)

        self.assertEqual(len(sla_1.tag_ids), 1)
        self.assertEqual(sla_1.tag_ids.name, "UPG:saas~17.1 helpdesk ticket type 1")

        self.assertEqual(len(sla_2.tag_ids), 2)
        self.assertIn(tag_1, sla_2.tag_ids)
        self.assertIn("UPG:saas~17.1 helpdesk ticket type 1", sla_2.tag_ids.mapped("name"))

        self.assertEqual(len(sla_3.tag_ids), 1)
        self.assertEqual(sla_3.tag_ids, tag_3)

        self.assertEqual(len(sla_4.tag_ids), 1)
        self.assertEqual(sla_4.tag_ids, tag_2)

        # check if the helpdesk ticket types data is correctly removed when we remove the model
        self.assertFalse(self.env.ref("helpdesk.model_helpdesk_ticket_type_action", raise_if_not_found=False))
        self.assertFalse(self.env.ref("helpdesk.type_question", raise_if_not_found=False))
        self.assertFalse(self.env.ref("helpdesk.type_incident", raise_if_not_found=False))
        self.assertFalse(self.env.ref("helpdesk.helpdesk_ticket_type_menu", raise_if_not_found=False))

        # Check if the domains are correctly adapted
        # Regex to get domain attribute of each filter
        domains_regex = re.compile(r"domain=\"(.*?)\"")

        ticket_search_view_domains = domains_regex.findall(ticket_search_view.arch)
        expected_ticket_search_view_domains = [
            [("tag_ids", "=", False)],
            [("tag_ids", "in", helpdesk_ticket_type1_tag.ids)],
            [("tag_ids", "in", ticket_type_tags.ids)],
            [("tag_ids", "ilike", "UPG:saas~17.1 %")],
            [("tag_ids", "in", tag_3.ids)],
            [(1, "=", 1)],  # TRUE
        ]
        for domain_str, expected_domain in zip(ticket_search_view_domains, expected_ticket_search_view_domains):
            domain = ast.literal_eval(domain_str)
            left, op, right = domain[0]
            expected_left, expected_op, expected_right = expected_domain[0]
            self.assertEqual(left, expected_left)
            self.assertEqual(op, expected_op)
            if isinstance(right, list):
                # sorted to have the elements in the same order
                self.assertListEqual(sorted(right), sorted(expected_right))
            else:
                self.assertEqual(right, expected_right)

        sla_search_view_domains = domains_regex.findall(sla_search_view.arch)
        expected_sla_search_view_domains = [
            [("tag_ids", "=", False)],
            [("tag_ids", "in", helpdesk_ticket_type1_tag.ids)],
            [("tag_ids", "in", ticket_type_tags.ids)],
            [("tag_ids", "ilike", "UPG:saas~17.1 %")],
            [("tag_ids", "in", tag_3.ids)],
            [("tag_ids.name", "ilike", "UPG:saas~17.1 %")],
            [("tag_ids", "in", helpdesk_ticket_type1_tag.ids)],
            [(1, "=", 1)],  # TRUE
        ]
        for domain_str, expected_domain in zip(sla_search_view_domains, expected_sla_search_view_domains):
            domain = ast.literal_eval(domain_str)
            left, op, right = domain[0]
            expected_left, expected_op, expected_right = expected_domain[0]
            self.assertEqual(left, expected_left)
            self.assertEqual(op, expected_op)
            if isinstance(right, list):
                # sorted to have the elements in the same order
                self.assertListEqual(sorted(right), sorted(expected_right))
            else:
                self.assertEqual(right, expected_right)
