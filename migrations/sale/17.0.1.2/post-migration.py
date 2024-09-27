from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "sale.report_saleorder_document", util.update_record_from_xml, reset_translations={"arch_db"})
    util.if_unchanged(
        cr, "sale.res_config_settings_view_form", util.update_record_from_xml, reset_translations={"arch_db"}
    )
