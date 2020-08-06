# -*- coding: utf-8 -*-


def migrate(cr, version):
    # remove field ref (field is still defined)
    cr.execute(
        """
            DELETE FROM ir_model_data
                  WHERE model = 'ir.model.fields'
                    AND res_id = (SELECT id
                                    FROM ir_model_fields
                                   WHERE model = 'project.project'
                                     AND name = 'allow_timesheets')
        """
    )
