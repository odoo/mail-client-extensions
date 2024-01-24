# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "crm.digest_tip_crm_0", util.update_record_from_xml, reset_translations={"tip_description"})
