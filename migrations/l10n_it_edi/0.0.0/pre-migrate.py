from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~18.2", "19.0") and util.table_exists(cr, "l10n_it_document_type"):
        script = util.import_script("l10n_it_edi_ndd/0.0.0/pre-migrate.py")
        script.check_and_report_duplicates(cr)
