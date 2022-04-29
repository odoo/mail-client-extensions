# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    mt_comment = env.ref("mail.mt_comment")
    if mt_comment:
        mt_comment.write({"track_recipients": True})
    mt_note = env.ref("mail.mt_note")
    if mt_note:
        mt_note.write({"track_recipients": True})
