# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "l10n_cl_edi_stock.l10n_cl_edi_email_template_picking", util.update_record_from_xml)
