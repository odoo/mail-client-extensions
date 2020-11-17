# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "website_forum.forum_post_template_new_answer", noupdate=True)
    util.force_noupdate(cr, "website_forum.forum_post_template_new_question", noupdate=True)
    util.force_noupdate(cr, "website_forum.forum_post_template_validation", noupdate=True)
