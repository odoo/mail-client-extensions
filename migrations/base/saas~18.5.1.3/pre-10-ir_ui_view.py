from odoo.upgrade import util


def migrate(cr, version):
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r"(<group[^>]*?)\sstring=([\"''])[^\"''<>]*\2"),
        util.PGRegexp(r"\1"),
        extra_filter="type = 'search' AND arch_db::TEXT LIKE '%%<group%%'",
    )

    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        util.PGRegexp(r"(<group[^>]*?)\sexpand=([\"''])[^\"''<>]*\2"),
        util.PGRegexp(r"\1"),
        extra_filter="type = 'search' AND arch_db::TEXT LIKE '%%<group%%'",
    )
