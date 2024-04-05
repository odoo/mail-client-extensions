from odoo.upgrade import util


def migrate(cr, version):
    # Necessary for industry_fsm_sale, if uninstalled it will be necessary anyway if
    # the client wants to install it later.
    # See enterprise/saas-17.1/industry_fsm_sale/views/project_project_views.xml#L56
    util.if_unchanged(
        cr, "sale_timesheet.project_project_view_form", util.update_record_from_xml, reset_translations={"arch_db"}
    )
