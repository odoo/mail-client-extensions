# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas~17."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    # for databases <= 10.saas-14
    util.rename_xmlid(cr, *util.expand_braces("{account_batch_deposit,base}.paperformat_batch_deposit"))

    util.move_model(cr, "report.paperformat", "report", "base", move_data=True)
    util.move_model(cr, "ir.qweb.field.barcode", "report", "base", move_data=False)
    util.remove_model(cr, "report")
    util.remove_model(cr, "report.abstract_report")

    for model in ["base.config.settings", "res.company"]:
        for field in ["paperformat_id", "external_report_layout"]:
            util.move_field_to_module(cr, model, field, "report", "base")

    remove = util.splitlines(
        """
        base_settings_view_form_inherit_report
        act_report_xml_view_inherit_report
        act_report_xml_view_inherit
        assets_backend

        # for databases <= 10.saas-14
        external_layout_header
        external_layout_footer
        minimal_layout
    """
    )
    for name in remove:
        util.remove_view(cr, "report." + name)

    util.force_noupdate(cr, "report.external_layout", False)

    move_to_web = util.splitlines(
        """
        assets_common
        assets_pdf
        assets_editor
        layout

        # other templates handled by `merge_module`
    """
    )
    for name in move_to_web:
        util.rename_xmlid(cr, "report." + name, "web.report_" + name, noupdate=False)

    cr.execute(
        """
        UPDATE ir_ui_view
           SET arch_db = regexp_replace(
                arch_db,
                't-call=([''"])report.(html_container|external_layout|internal_layout|basic_layout)\1',
                't-call=\1web.\2\1',
                'g')
         WHERE type='qweb'
    """
    )

    util.rename_xmlid(cr, "report.view_company_report_form", "base.view_company_report_form")
    util.merge_module(cr, "report", "web", without_deps=True)

    util.remove_record(cr, "base.preview_rml_report")
    # now adapt model
    util.rename_model(cr, "ir.actions.report.xml", "ir.actions.report", rename_table=False)
    cr.execute("UPDATE ir_actions SET type='ir.actions.report' WHERE type='ir.actions.report.xml'")

    cr.execute(
        """
        SELECT name
          FROM ir_act_report_xml
         WHERE report_type IN ('controller', 'pdf', 'sxw', 'webkit')
    """
    )
    reports = "\n".join(" - %s" % n for n, in cr.fetchall())
    if reports:
        msg = "The database still contains deprecated reports:\n%s" % reports
        _logger.warning(msg)
        util.add_to_migration_reports(msg, "Reporting")

    remove = util.splitlines(
        """
        header
        parser
        auto
        report_xml
        report_xsl
        report_rml
        report_sxw_content_data
        report_rml_content_data
    """
    )
    for field in remove:
        util.remove_field(cr, "ir.actions.report", field, drop_column=not reports)
