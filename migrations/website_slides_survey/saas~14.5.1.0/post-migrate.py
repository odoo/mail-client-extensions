# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "website_slides_survey.mail_template_user_input_certification_failed", util.update_record_from_xml
    )
