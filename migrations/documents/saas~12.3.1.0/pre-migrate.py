# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "email_cc", "varchar")
    util.create_column(cr, "documents_request_wizard", 'partner_id', 'int4')
