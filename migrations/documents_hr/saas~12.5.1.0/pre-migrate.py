# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("documents{,_hr}.documents_hr_folder"))
    util.rename_xmlid(cr, *eb("documents{,_hr}.documents_hr_documents"))
    util.rename_xmlid(cr, *eb("documents{,_hr}.documents_hr_documents_absences"))

    util.delete_unused(cr, "documents_tag", {"documents.documents_hr_documents_appraisal"})
