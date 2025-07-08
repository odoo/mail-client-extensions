from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_my_edi.ir_cron_myinvois_sync")
    util.remove_model(cr, "l10n_my_edi.document.status.update")
    util.remove_record(cr, "l10n_my_edi.l10n_my_edi_document_status_update_form")
