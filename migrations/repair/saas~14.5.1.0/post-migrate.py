# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "repair.mail_template_repair_quotation", util.update_record_from_xml)
