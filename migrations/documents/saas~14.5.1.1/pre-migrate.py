# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_folder", "user_specific_write", "bool")

    util.update_record_from_xml(cr, "documents.documents_document_write_rule")
