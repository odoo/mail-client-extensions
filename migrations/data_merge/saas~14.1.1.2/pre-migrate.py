# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "data_merge.merge_message", "data_merge.data_merge_merged")
    util.rename_xmlid(cr, "data_merge.merge_message_master", "data_merge.data_merge_main")
    util.rename_xmlid(cr, "data_merge.notification", "data_merge.data_merge_duplicate")
