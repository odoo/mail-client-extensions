# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Prevents constraint mail_channel_partner_partner_unique from failing
    if util.version_gte("saas~15.1"):
        # table mail_channel_partner was renamed to mail_channel_member in 15.5
        name = "member" if util.table_exists(cr, "mail_channel_member") else "partner"
        # table mail_channel_member was renamed to discuss_channel_member in 16.3
        prefix = "discuss" if util.table_exists(cr, "discuss_channel_member") else "mail"
        util.ensure_xmlid_match_record(
            cr,
            "mail.channel_{}_general_channel_for_admin".format(name),
            "{0}.channel.{1}".format(prefix, name),
            {
                "partner_id": util.ref(cr, "base.partner_admin"),
                "channel_id": util.ref(cr, "mail.channel_all_employees"),
            },
        )
