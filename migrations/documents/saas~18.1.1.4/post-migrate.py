from odoo.upgrade import util


def migrate(cr, version):
    # force creation of `forcecreate=0` record
    if not util.version_gte("saas~18.5"):
        util.update_record_from_xml(cr, "documents.document_administrator_folder")
        # and reset it `noupdate` flag (including parent record)
        util.force_noupdate(cr, "documents.document_administrator_folder", noupdate=True)
        util.force_noupdate(cr, "documents.document_administrator_folder_mail_alias", noupdate=True)
