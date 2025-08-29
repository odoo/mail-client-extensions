from odoo.upgrade import util


def migrate(cr, version):
    # Add page options to COWed layouts
    cr.execute(
        r"""
        SELECT v.id
          FROM ir_ui_view v
     LEFT JOIN ir_model_data d
            ON d.model = 'ir.ui.view'
           AND d.res_id = v.id
         WHERE d.id IS NULL
           AND v.key = 'website.layout'
           AND v.arch_db::text NOT LIKE '%o\_frontend\_to\_backend\_buttons%'
    """
    )
    view_ids = cr.fetchall()
    if view_ids:
        standard_view = util.ref(cr, "website.layout")
        with util.edit_view(cr, view_id=standard_view, active=None) as std_arch:
            page_options = std_arch.xpath("//xpath[.//*[contains(@class,'o_frontend_to_backend_buttons')]]")[0]
        for view in view_ids:
            with util.edit_view(cr, view_id=view, active=None) as arch:
                arch.append(page_options)
