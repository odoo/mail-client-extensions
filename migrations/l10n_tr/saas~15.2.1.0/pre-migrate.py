from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_tr.l10ntr_tek_duzen_hesap", "l10n_tr.chart_template_common")
