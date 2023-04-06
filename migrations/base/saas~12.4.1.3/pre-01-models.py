# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "ir_module_module_dependency", "auto_install_required", "boolean")
    cr.execute("UPDATE ir_module_module_dependency SET auto_install_required = TRUE")
    cr.execute(
        """
        ALTER TABLE ir_module_module_dependency
       ALTER COLUMN auto_install_required
        SET DEFAULT TRUE
    """
    )

    # Actions
    cr.execute("UPDATE ir_actions SET binding_type = 'action' WHERE binding_type = 'action_form_only'")
    util.create_column(cr, "ir_actions", "binding_view_types", "varchar")  # TODO check with @xmo on how to fill it.
    cr.execute(
        """
        UPDATE ir_actions a
           SET binding_view_types = CASE WHEN w.multi THEN 'list' ELSE 'list,form' END
          FROM ir_act_window w
         WHERE w.id = a.id
           AND a.binding_view_types IS NULL
        """
    )
    cr.execute("UPDATE ir_actions SET binding_view_types = 'list,form' WHERE binding_view_types IS NULL")
    util.update_field_usage(cr, "ir.actions.act_window", "src_model", "binding_model_id.model")
    util.remove_field(cr, "ir.actions.act_window", "src_model")
    util.remove_field(cr, "ir.actions.act_window", "auto_search")
    util.remove_field(cr, "ir.actions.act_window", "multi")

    # Remove attachment's datas_fname
    # We must keep the name for cached xsd of mx localisation.
    # See https://github.com/odoo/enterprise/pull/4215/files#r290596761
    cr.execute(
        """
        UPDATE ir_attachment
           SET name = datas_fname
         WHERE datas_fname IS NOT NULL
           AND name != datas_fname
           AND name NOT ILIKE 'xsd__cached__%'
    """
    )
    util.update_field_usage(cr, "ir.attachment", "datas_fname", "name")
    util.remove_field(cr, "ir.attachment", "datas_fname")

    # steal fields from `base_geolocalize` module
    util.move_field_to_module(cr, "res.partner", "partner_latitude", "base_geolocalize", "base")
    util.move_field_to_module(cr, "res.partner", "partner_longitude", "base_geolocalize", "base")
