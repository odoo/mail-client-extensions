# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "slide.channel.invite", "email_from")
    util.remove_field(cr, "slide.channel.invite", "author_id")
