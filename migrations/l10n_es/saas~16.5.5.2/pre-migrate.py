# -*- coding: utf-8 -*-
from odoo.upgrade import util

tag_migration_utils = util.import_script("l10n_mn/saas~16.5.1.1/pre-migrate.py")

def migrate(cr, version):
    # Remove old reports
    util.remove_record(cr, "l10n_es_reports.mod_111")
    util.remove_record(cr, "l10n_es_reports.mod_115")
    util.remove_record(cr, "l10n_es_reports.mod_303")
    tag_migration_utils.disable_obsolete_tax_tag(cr, "l10n_es.mod_303_61")
