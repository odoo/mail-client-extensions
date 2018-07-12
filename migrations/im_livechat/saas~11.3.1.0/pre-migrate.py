# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for s in {0, 1, 5, 10}:
        util.remove_record(cr, "im_livechat.mail_shortcode_rating_%s" % s)
