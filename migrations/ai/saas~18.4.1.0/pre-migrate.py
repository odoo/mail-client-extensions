from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "ai.open_view_ai_composer_kanban", "ai.ai_composer_action")
