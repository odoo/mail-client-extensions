# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_mass_mailing.s_mail_block_header_social")
    util.remove_view(cr, "website_mass_mailing.s_mail_block_header_text_social")
