# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # some customers remove and recreate data ICP.
    util.ensure_xmlid_match_record(
        cr, "mail.icp_mail_catchall_alias", "ir.config_parameter", {"key": "mail.catchall.alias"}
    )
    util.ensure_xmlid_match_record(
        cr, "mail.icp_mail_bounce_alias", "ir.config_parameter", {"key": "mail.bounce.alias"}
    )
