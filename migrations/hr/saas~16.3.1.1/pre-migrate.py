# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr.view_partner_tree2")
    # Rename mail.channel to discuss.channel
    # NOTE: the trailing `_` is NOT a typo.
    util.rename_xmlid(cr, "hr.mail_channel_view_form_", "hr.discuss_channel_view_form")
