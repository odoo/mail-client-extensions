# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for color_field in {"header_background", "title", "button_background", "button_text"}:
        util.create_column(cr, "im_livechat_channel", f"{color_field}_color", "varchar")

    cr.execute(
        """
        UPDATE im_livechat_channel
           SET header_background_color = '#875A7B',
               title_color = '#FFFFFF',
               button_background_color = '#878787',
               button_text_color = '#FFFFFF'
    """
    )
