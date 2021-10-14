# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing.s_mail_block_banner")
    util.remove_view(cr, "mass_mailing.s_mail_block_paragraph")
    util.remove_view(cr, "mass_mailing.s_mail_block_title_sub")
    util.remove_view(cr, "mass_mailing.s_mail_block_comparison_table")
    util.remove_view(cr, "mass_mailing.s_mail_block_two_cols")
    util.remove_view(cr, "mass_mailing.s_mail_block_three_cols")
    util.remove_view(cr, "mass_mailing.s_mail_block_image_text")
    util.remove_view(cr, "mass_mailing.s_mail_block_text_image")
    util.remove_view(cr, "mass_mailing.s_mail_block_image")
    util.remove_view(cr, "mass_mailing.s_mail_block_footer_separator")
    util.remove_view(cr, "mass_mailing.s_mail_block_discount2")
    util.remove_view(cr, "mass_mailing.s_mail_block_steps")
