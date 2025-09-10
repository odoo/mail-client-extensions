from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb("l10n_it_{xml_export,reports}.monthly.tax.report.xml.export.wizard"))
    util.remove_field(cr, "l10n_it_reports.monthly.tax.report.xml.export.wizard", "subcontracting")
    util.remove_field(cr, "l10n_it_reports.monthly.tax.report.xml.export.wizard", "exceptional_events")
    util.remove_field(cr, "l10n_it_reports.monthly.tax.report.xml.export.wizard", "extraordinary_operations")
