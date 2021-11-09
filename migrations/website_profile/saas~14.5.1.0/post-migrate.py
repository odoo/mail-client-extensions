# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "website_profile.validation_email", util.update_record_from_xml, reset_translations={"subject", "body_html"}
    )
