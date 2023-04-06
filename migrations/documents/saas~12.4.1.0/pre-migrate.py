# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_field_usage(cr, "documents.document", "datas_fname", "attachment_name")
    util.remove_field(cr, "documents.document", "datas_fname")
