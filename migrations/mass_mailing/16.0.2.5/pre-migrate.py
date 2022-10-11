# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing.s_mail_block_event")
    util.remove_view(cr, "mass_mailing.s_mail_block_footer_tag_line")
    util.remove_view(cr, "mass_mailing.s_mail_block_title_text")
    util.if_unchanged(cr, "mass_mailing.mass_mailing_mail_style", util.update_record_from_xml)
    cr.execute("UPDATE ir_model_data SET noupdate=false WHERE module='mass_mailing' AND model='ir.attachment'")
