# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "is_canned_response")
    util.remove_field(cr, "helpdesk.team", "feature_livechat_web_page")
