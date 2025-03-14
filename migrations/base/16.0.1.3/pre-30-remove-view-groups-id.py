def migrate(cr, version):
    cr.execute(
        """
            DELETE FROM ir_ui_view_group_rel rel
                  USING ir_ui_view view
                  WHERE rel.view_id = view.id
                    AND view.inherit_id IS NOT NULL
                    AND view.mode != 'primary'
        """
    )
