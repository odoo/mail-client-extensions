# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_presence.mail_template_presence", util.update_record_from_xml)
