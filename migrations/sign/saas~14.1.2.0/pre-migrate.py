# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_send_request", "activity_id", "int4")
    util.create_column(cr, "sign_send_request", "has_default_template", "boolean")
