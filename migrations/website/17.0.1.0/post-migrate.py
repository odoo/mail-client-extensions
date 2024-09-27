from odoo.upgrade import util


def migrate(cr, version):
    view = util.env(cr).ref("website.no_autohide_menu")
    cr.execute(
        """
        SELECT h.website_id
          FROM ir_ui_view h
     LEFT JOIN ir_ui_view a
            ON h.website_id = a.website_id
           AND a.key = 'website.no_autohide_menu'
           AND a.active
         WHERE h.key = 'website.template_header_hamburger'
           AND h.active
           AND a.id is NULL
      GROUP BY h.website_id
        """
    )
    for (website_id,) in cr.fetchall():
        view.copy({"website_id": website_id, "active": True})
    util.if_unchanged(
        cr, "website.res_config_settings_view_form", util.update_record_from_xml, reset_translations={"arch_db"}
    )
