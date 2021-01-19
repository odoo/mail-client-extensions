# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_tag_category", "is_published", "boolean", default=True)
