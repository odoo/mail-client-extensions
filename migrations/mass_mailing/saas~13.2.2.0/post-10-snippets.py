# -*- coding: utf-8 -*-
import odoo.upgrade.util.snippets as snip


def migrate(cr, version):
    snippets = [
        snip.Snippet("s_mail_block_header_social", "div", "o_mail_block_header_social"),
        snip.Snippet("s_mail_block_header_text_social", "div", "o_mail_block_header_text_social"),
        snip.Snippet("s_mail_block_header_logo", "div", "o_mail_block_header_logo"),
        snip.Snippet("s_mail_block_banner", "div", "o_mail_block_banner"),
        snip.Snippet("s_mail_block_title_text", "div", "o_mail_block_title_text"),
        snip.Snippet("s_mail_block_paragraph", "div", "o_mail_block_paragraph"),
        snip.Snippet("s_mail_block_title_sub", "div", "o_mail_block_title_sub"),
        snip.Snippet("s_mail_block_comparison_table", "o_mail_block_comparison_table"),
        snip.Snippet("s_mail_block_two_cols", "div", "o_mail_block_two_cols"),
        snip.Snippet("s_mail_block_three_cols", "div", "o_mail_block_three_cols"),
        snip.Snippet("s_mail_block_image_text", "div", "o_mail_block_image_text"),
        snip.Snippet("s_mail_block_text_image", "div", "o_mail_block_text_image"),
        snip.Snippet("s_mail_block_image", "div", "o_mail_block_image"),
        snip.Snippet("s_mail_block_footer_separator", "div", "o_mail_block_footer_separator"),
        snip.Snippet("s_mail_block_footer_tag_line", "div", "o_mail_block_footer_tag_line"),
        snip.Snippet("s_mail_block_discount2", "div", "o_mail_block_discount2"),
        snip.Snippet("s_mail_block_discount1", "div", "o_mail_block_discount1"),
        snip.Snippet("s_mail_block_event", "div", "o_mail_block_event"),
        snip.Snippet("s_mail_block_steps", "div", "o_mail_block_steps"),
        snip.Snippet("s_mail_block_footer_social", "div", "o_mail_footer_social_center"),
        snip.Snippet("s_mail_block_footer_social_left", "div", "o_mail_footer_social_left"),
    ]

    regex = snip.get_regex_from_snippets_list(snippets)
    snip.add_snippet_names_on_html_field(cr, "mailing_mailing", "body_html", snippets, regex)
    snip.add_snippet_names_on_html_field(cr, "mailing_mailing", "body_arch", snippets, regex)
