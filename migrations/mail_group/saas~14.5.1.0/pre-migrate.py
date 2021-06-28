# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Rename <mail.moderation> to <mail.group.moderation> and update reference field
    util.rename_model(cr, "mail.moderation", "mail.group.moderation")
    cr.execute("ALTER TABLE mail_group_moderation DROP CONSTRAINT IF EXISTS mail_group_moderation_channel_id_fkey")
    util.rename_field(cr, "mail.group.moderation", "channel_id", "mail_group_id")
    # Because table `mail_group` is not filled yet ORM will not be able to set
    # any FK and will crash. We will do it ourselves in the `post-` script.
    cr.execute("ALTER TABLE mail_group_moderation RENAME COLUMN mail_group_id TO _mail_group_id")
    util.create_column(cr, "mail_group_moderation", "mail_group_id", "int4")

    # Update <mail.group.moderation>: make mail_group owner of model
    util.move_model(cr, "mail.group.moderation", "mail", "mail_group")
    for xml_part in "action menu view_tree view_search".split():
        util.rename_xmlid(cr, f"mail.mail_moderation_{xml_part}", f"mail_group.mail_group_moderation_{xml_part}")
