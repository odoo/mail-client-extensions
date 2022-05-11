# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Now a dynamic view. See https://github.com/odoo/odoo/pull/56080
    cr.execute("DROP VIEW IF EXISTS crm_partner_report_assign")
