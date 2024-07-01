from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "project_enterprise.project_task_view_form", util.update_record_from_xml, reset_translations={"arch_db"}
    )
