from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "knowledge.knowledge_article_user_onboarding", util.update_record_from_xml)
    util.update_record_from_xml(cr, "knowledge.knowledge_article_mail_invite")
