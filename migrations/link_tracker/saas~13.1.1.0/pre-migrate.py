# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "link.tracker", "favicon")
    util.remove_field(cr, "link.tracker", "icon_src")
