from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents.document_administrator_folder", util.update_record_from_xml)
