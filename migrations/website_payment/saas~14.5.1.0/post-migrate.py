# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_payment.mail_template_donation", util.update_record_from_xml)
