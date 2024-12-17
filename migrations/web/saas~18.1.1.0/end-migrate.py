from odoo.upgrade import util


def migrate(cr, version):
    # Rename DynamicModelFieldSelectorChar widget to field_selector in all views
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        # widget="DynamicModelFieldSelectorChar" or widget='DynamicModelFieldSelectorChar'
        util.PGRegexp(r"""widget=(['"])DynamicModelFieldSelectorChar\1"""),
        r"widget=\1field_selector\1",
    )
