# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "pos_coupon.mail_coupon_template", util.update_record_from_xml, reset_translations={"subject", "body_html"}
    )
