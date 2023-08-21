# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~14.5"):
        match(cr, "base")


def match(cr, module):
    # some customers remove and recreate data ICP.
    util.ensure_xmlid_match_record(
        cr, module + ".icp_mail_catchall_alias", "ir.config_parameter", {"key": "mail.catchall.alias"}
    )
    util.ensure_xmlid_match_record(
        cr, module + ".icp_mail_bounce_alias", "ir.config_parameter", {"key": "mail.bounce.alias"}
    )
    if util.version_gte("saas~14.5"):
        util.ensure_xmlid_match_record(
            cr, module + ".icp_mail_default_from", "ir.config_parameter", {"key": "mail.default.from"}
        )
