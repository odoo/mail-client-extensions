# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.remove_module(cr, "event_barcode_mobile")
        util.remove_module(cr, "hr_attendance_mobile")
        util.remove_module(cr, "barcodes_mobile")
