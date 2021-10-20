from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~12.3"):
        cr.execute(
            """
                UPDATE ir_ui_view view
                   SET arch_updated = false
                  FROM theme_ir_ui_view template
                 WHERE view.theme_template_id IS NOT NULL
                   AND template.id = view.theme_template_id
                   AND view.arch_db = template.arch
            """
        )
