# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "digest.digest", "template_id")
    util.remove_record(cr, "digest.digest_mail_template")

    util.update_record_from_xml(cr, "digest.digest_mail_main")
    util.update_record_from_xml(cr, "digest.digest_mail_layout")
    util.update_record_from_xml(cr, "digest.digest_tip_digest_0")
    util.update_record_from_xml(cr, "digest.digest_tip_digest_1")
    util.update_record_from_xml(cr, "digest.digest_tip_digest_2")
    util.update_record_from_xml(cr, "digest.digest_tip_digest_3")
    util.remove_record(cr, "digest.digest_tip_mail_0")
    util.remove_record(cr, "digest.digest_tip_mail_1")
    util.remove_record(cr, "digest.digest_tip_mail_2")
