# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_request", "refusal_allowed", "boolean")
    util.create_column(cr, "sign_send_request", "refusal_allowed", "boolean")
    util.create_column(cr, "sign_template", "num_pages", "integer", default=None)
