# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale_gift_card.mail_template_gift_card", util.update_record_from_xml)
