# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "social_account", "company_id", "int4")
    util.create_column(cr, "social_post", "company_id", "int4")
    util.create_column(cr, "social_stream", "company_id", "int4")
