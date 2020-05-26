# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "digest.digest", "template_id")
    util.remove_record(cr, "digest.digest_mail_template")
