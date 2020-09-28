from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{base,web}.view_base_document_layout"))
    util.rename_xmlid(cr, *eb("{base,web}.access_base_document_layout"))
    util.rename_xmlid(cr, *eb("{base,web}.action_base_document_layout_configurator"))
    util.remove_view(cr, "base.layout_preview")

    util.move_model(cr, "base.document.layout", "base", "web")
    util.create_column(cr, "report_layout", "sequence", "integer")
    cr.execute("UPDATE report_layout SET sequence = id")

    util.rename_xmlid(cr, *eb("base.module_category_{localization,accounting_localizations}_account_charts"))
    util.remove_record(cr, "base.module_category_localization")
    util.remove_record(cr, "base.module_category_operations")
