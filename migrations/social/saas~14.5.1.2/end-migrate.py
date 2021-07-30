# -*- coding: utf-8 -*-

from odoo.tools import html2plaintext

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)

    for social_media in env["social.media"].search([]):
        social_media.media_description = html2plaintext(social_media.media_description).strip()
