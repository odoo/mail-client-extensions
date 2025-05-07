from odoo.upgrade import util


def migrate(cr, version):
    # force folder and alias in noupdate (match xml declaration)
    util.force_noupdate(cr, "documents.document_administrator_folder", noupdate=True)
    util.force_noupdate(cr, "documents.document_administrator_folder_mail_alias", noupdate=True)
