# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Let Odoo auto-generate the field "account_ids" on the "social.post" model
    # (which inherits now from "social.post.template")
    cr.execute("ALTER TABLE social_post_social_account RENAME COLUMN post_id TO social_post_id")
    cr.execute("ALTER TABLE social_post_social_account RENAME COLUMN account_id TO social_account_id")
    cr.execute("ALTER TABLE social_post_social_account RENAME TO social_account_social_post_rel")

    util.remove_view(cr, "social.social_post_view_form")
