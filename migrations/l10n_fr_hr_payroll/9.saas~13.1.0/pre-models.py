# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr,
                      'report.l10n_fr_hr_payroll.report_l10nfrfichepaye',
                      'report.l10n_fr_hr_payroll.report_l10n_fr_fiche_paye',rename_table=False)

    util.rename_xmlid(cr,
                      'l10n_fr_hr_payroll.report_l10nfrfichepaye',
                      'l10n_fr_hr_payroll.report_l10n_fr_fiche_paye')

    util.remove_view(cr, 'l10n_fr_hr_payroll.res_company_form_l10n_fr_payroll')
