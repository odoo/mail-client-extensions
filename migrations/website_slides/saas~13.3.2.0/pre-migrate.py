# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "slide_channel_tag", "color", "int4")

    cr.execute("UPDATE slide_channel_tag SET color = 0")
