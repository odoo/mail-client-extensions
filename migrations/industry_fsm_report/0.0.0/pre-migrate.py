from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.convert_bootstrap import convert_tree


def migrate(cr, version):
    if util.version_between("16.0", "18.0"):
        cr.execute(
            """
            SELECT view.id
              FROM ir_ui_view view
              JOIN ir_model_data imd
                ON imd.res_id = view.id
             WHERE imd.name ILIKE 'report_custom_x_project_task_worksheet%'
               AND imd.module = 'industry_fsm_report'
               AND view.type = 'qweb'
            """
        )
        for (view_id,) in cr.fetchall():
            with util.edit_view(cr, view_id=view_id, active=None) as arch:
                convert_tree(arch, "4.0", "5.0", is_qweb=True)
