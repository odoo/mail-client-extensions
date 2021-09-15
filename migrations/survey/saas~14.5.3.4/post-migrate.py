# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "survey.mail_template_user_input_invite", util.update_record_from_xml)
    util.if_unchanged(cr, "survey.mail_template_certification", util.update_record_from_xml)
