# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # This loop force updates the data records from "base.res_partner_industry_A" to "base.res_partner_industry_U"
    for i in range(65, 86):
        util.if_unchanged(cr, "base.res_partner_industry_" + chr(i), util.update_record_from_xml)
