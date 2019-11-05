# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "rating_rating", "publisher_comment", "text")
    util.create_column(cr, "rating_rating", "publisher_id", "int4")
    util.create_column(cr, "rating_rating", "publisher_datetime", "timestamp without time zone")
