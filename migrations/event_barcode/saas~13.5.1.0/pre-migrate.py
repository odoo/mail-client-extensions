# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "event_barcode.event_event_view_form_inherit_barcode",
                      "event_barcode.event_event_view_form")
