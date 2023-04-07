# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "im_livechat.mail_shortcode_data_hello", util.update_record_from_xml)
    util.if_unchanged(cr, "im_livechat.mail_canned_response_bye", util.update_record_from_xml)
