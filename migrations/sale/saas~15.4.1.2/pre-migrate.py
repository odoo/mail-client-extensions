# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Now a dynamic view. See https://github.com/odoo/odoo/pull/83550
    cr.execute("DROP VIEW IF EXISTS sale_report")
