# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "sign.request", "folder_id")
    util.remove_field(cr, "sign.request", "documents_tag_ids")
