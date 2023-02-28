# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "knowledge.knowledge_article_user_onboarding", util.update_record_from_xml)
    util.if_unchanged(cr, "knowledge.knowledge_article_hr_faq", util.update_record_from_xml)
    util.if_unchanged(cr, "knowledge.knowledge_article_sales_and_marketing", util.update_record_from_xml)
    util.if_unchanged(cr, "knowledge.knowledge_article_sales_playbook", util.update_record_from_xml)
    util.if_unchanged(cr, "knowledge.knowledge_article_brand_assets", util.update_record_from_xml)
