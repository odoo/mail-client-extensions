# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Prevents constraint mail_channel_partner_partner_unique from failing
    if util.version_gte("saas~15.1"):
        util.ensure_xmlid_match_record(
            cr,
            "mail.channel_partner_general_channel_for_admin",
            "mail.channel.partner",
            {
                "partner_id": util.ref(cr, "base.partner_admin"),
                "channel_id": util.ref(cr, "mail.channel_all_employees"),
            },
        )
