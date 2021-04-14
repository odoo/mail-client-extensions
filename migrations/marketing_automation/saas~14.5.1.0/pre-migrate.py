# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "marketing.trace", "sent")
    util.remove_field(cr, "marketing.trace", "exception")
    util.remove_field(cr, "marketing.trace", "opened")
    util.remove_field(cr, "marketing.trace", "replied")
    util.remove_field(cr, "marketing.trace", "bounced")

    util.rename_field(cr, "marketing.trace", "clicked", "links_click_datetime")
