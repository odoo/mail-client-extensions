from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "knowledge.knowledge_template_my_todo_list", util.remove_record)
    util.delete_unused(cr, "knowledge.knowledge_article_template_category_recommended")
    util.if_unchanged(cr, "knowledge.knowledge_article_template_hr_faq", util.update_record_from_xml)
    util.if_unchanged(cr, "knowledge.knowledge_article_template_brand_assets", util.update_record_from_xml)
    util.delete_unused(cr, "knowledge.knowledge_article_template_category_sales_and_marketing")
    util.if_unchanged(
        cr, "knowledge.knowledge_article_template_category_company_organization", util.update_record_from_xml
    )
