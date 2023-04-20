# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    # Rename mail.channel to discuss.channel
    util.rename_field(cr, "website.visitor", *eb("{mail,discuss}_channel_ids"))
