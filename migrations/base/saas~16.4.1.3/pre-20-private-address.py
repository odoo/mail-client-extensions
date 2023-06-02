# -*- coding: utf-8 -*-

import os
from pathlib import Path

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "base.group_private_addresses")
    util.remove_record(cr, "base.res_partner_rule_private_employee")
    util.remove_record(cr, "base.res_partner_rule_private_group")

    util._logger.log(
        util.NEARLYWARN,
        """
The 'private' type has been removed from res.partner model.
Note that instead only archiving the existing private partners, it is
possible to directly migrate them into a specific table, only available
for administrators, by setting an 'UPG_RECYCLE_PRIVATE_PARTNERS' env variable.""",
    )

    if util.str2bool(os.getenv("UPG_RECYCLE_PRIVATE_PARTNERS", "0")):
        handling_other_addresses_message = """
    <li>Handling other private addresses:
        <ul>
            <li>Private addresses not linked to a specific standard flow were recycled and moved to another table.</li>
            <li>The new table, exclusively available to administrators, provides a dedicated space to manage these specific pieces of information.</li>
        </ul>
    </li>
        """
        button_message = ""
    else:
        handling_other_addresses_message = """
    <li>Handling other private addresses:
        <ul>
            <li>Private addresses not linked to a specific standard flow were archived and marked with the "Old Private Address" tag.</li>
            <li>These archived addresses are still accessible but are separated from the main data flow.</li>
            <li>Customers have the flexibility to either keep them as archived, treat them differently, or initiate a recycling loop.</li>
            <li>By clicking on the button below, the customer can trigger a recycling process to move these private addresses to another table.</li>
            <li>The new table, exclusively available to administrators, provides a dedicated space to manage these specific pieces of information.</li>
        </ul>
    </li>
"""
        button_message = """
<p style="margin: 16px 0px 16px 0px; text-align: center;">
    <a href="/web?debug=1#action=base.ir_action_activate_private_address_recycling" style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Recycle Private Addresses</a>
</p>
"""

    util.add_to_migration_reports(
        f"""
<ul>
    <li>The private addresses have been removed from the "res.partner" model.</li>
    <li>The employees' private address information has been moved to the "hr.employee" model, preserving the old records but emptying the private information fields.</li>
    <li>The applicant's private address information has been moved to the "hr.applicant" model, following the same approach.</li>
</ul>
<strong>Actions taken:</strong>
<ul>
    <li>Private addresses from the "res.partner" model:
        <ul>
            <li>Private addresses were identified and removed from the "res.partner" model.</li>
            <li>This step ensures that private address information is no longer stored in the "res.partner" model.</li>
        </ul>
    </li>
    <li>Employees' private address information:
        <ul>
            <li>To improve data organization, employees' private address information has been transferred to the "hr.employee" model.</li>
            <li>The existing records in the "res.partner" model were preserved but emptied of any private information.</li>
            <li>The transfer ensures that private addresses are now associated with the respective employees.</li>
        </ul>
    </li>
    <li>Applicant's private address information:
        <ul>
            <li>Similarly, private address information for applicants has been moved to the "hr.applicant" model.</li>
            <li>By doing so, each applicant's private address is now linked to their corresponding application.</li>
        </ul>
    </li>
    {handling_other_addresses_message}
</ul>
{button_message}
""",
        "Private Addresses Removal",
        format="html",
    )

    f = Path(__file__).parent / "recycle_private_partners.py"
    # Avoid unsafe imports opcodes at the beginning of the file
    recycle_code = f.read_text().partition("# END OF IMPORTS")[2].strip()
    code = f"""\
{recycle_code}

recycle(env)
action = env['ir.actions.act_window']._for_xml_id('base.action_x_res_partner_private')
"""

    cr.execute(
        """
        INSERT INTO ir_act_server (
            name, usage, state, model_id, model_name, code, type, binding_type)
        VALUES (
            jsonb_build_object('en_US', 'Base: Activate Private Address Recycling'),
            'ir_actions_server',
            'code',
            %s,
            'ir.actions.server',
            %s,
            'ir.actions.server',
            'action'
        )
        RETURNING id
        """,
        (
            util.ref(cr, "base.model_ir_actions_server"),
            code,
        ),
    )

    [server_action_id] = cr.fetchone()
    cr.execute(
        """
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            "base",
            "ir_action_activate_private_address_recycling",
            "ir.actions.server",
            server_action_id,
            True,
        ),
    )
