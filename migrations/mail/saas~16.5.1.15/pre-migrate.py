# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # alias views renaming
    for pre, post in [
        ("view_mail_alias_form", "mail_alias_view_form"),
        ("view_mail_alias_tree", "mail_alias_view_tree"),
        ("view_mail_alias_search", "mail_alias_view_search"),
        ("action_view_mail_alias", "mail_alias_action"),
    ]:
        util.rename_xmlid(cr, f"mail.{pre}", f"mail.{post}")

    # ICP move
    for xml_id in [
        "icp_mail_catchall_alias",
        "icp_mail_bounce_alias",
        "icp_mail_default_from",
    ]:
        util.rename_xmlid(cr, f"base.{xml_id}", f"mail.{xml_id}", on_collision="merge")
