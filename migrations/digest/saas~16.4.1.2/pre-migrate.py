# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "digest.digest_mail_layout", util.update_record_from_xml)
