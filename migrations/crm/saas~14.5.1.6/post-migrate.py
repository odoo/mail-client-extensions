# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "crm.mail_template_demo_crm_lead", util.update_record_from_xml)

    util.if_unchanged(cr, "crm.digest_tip_crm_0", util.update_record_from_xml)
