# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Prevents constraint mail_channel_partner_partner_unique from failing
    if util.version_gte("saas~15.1"):
        if util.table_exists(cr, "discuss_channel_member"):
            # >= saas~16.3
            prefix, name = "discuss", "member"
        elif util.table_exists(cr, "mail_channel_member"):
            # >= saas~15.5
            prefix, name = "mail", "member"
        else:
            prefix, name = "mail", "partner"

        util.ensure_xmlid_match_record(
            cr,
            "mail.channel_{}_general_channel_for_admin".format(name),
            "{}.channel.{}".format(prefix, name),
            {
                "partner_id": util.ref(cr, "base.partner_admin"),
                "channel_id": util.ref(cr, "mail.channel_all_employees"),
            },
        )
