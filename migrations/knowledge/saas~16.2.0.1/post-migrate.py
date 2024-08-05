from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "knowledge.knowledge_article_view_kanban", util.update_record_from_xml, reset_translations={"arch_db"}
    )
