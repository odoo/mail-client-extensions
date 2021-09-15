# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "portal.mail_template_data_portal_welcome", util.update_record_from_xml)
