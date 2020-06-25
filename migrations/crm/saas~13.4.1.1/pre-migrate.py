# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "partner_address_email")
    util.remove_view(cr, "crm.assets_tests")

    util.update_record_from_xml(cr, "crm.digest_tip_crm_0")
    util.update_record_from_xml(cr, "crm.digest_tip_crm_1")
    util.update_record_from_xml(cr, "crm.digest_tip_crm_2")
