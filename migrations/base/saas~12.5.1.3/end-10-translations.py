# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_translation t
           SET type = 'model',
               name = 'ir.model.fields.selection,name',
               res_id = s.id
          FROM ir_model_fields_selection s
    INNER JOIN ir_model_fields f ON s.field_id=f.id
    INNER JOIN ir_model m ON m.id=f.model_id
         WHERE t.type = 'selection'
           AND s.name = t.src
           AND split_part(t.name,',',1)=m.model
           AND split_part(t.name,',',2)=f.name
AND NOT EXISTS (SELECT 1
                  FROM ir_translation
                 WHERE type = 'model'
                   AND name = 'ir.model.fields.selection,name'
                   AND res_id = s.id
                   AND lang = t.lang)
    """
    )

    cr.execute(
        """
            DELETE FROM ir_translation WHERE id IN (
                SELECT unnest((array_agg(id ORDER BY id))[2:])
                  FROM ir_translation
                 WHERE type IN ('constraint', 'sql_constraint')
              GROUP BY src, lang
                HAVING count(*) > 1
            )
    """
    )
    cr.execute(
        """
        UPDATE ir_translation t
           SET type = 'model',
               name = 'ir.model.constraint,message',
               res_id = c.id
          FROM ir_model_constraint c
         WHERE t.type IN ('constraint', 'sql_constraint')
           AND c.message = t.src
AND NOT EXISTS (SELECT 1
                  FROM ir_translation
                 WHERE type = 'model'
                   AND name = 'ir.model.constraint,message'
                   AND res_id = c.id
                   AND lang = t.lang)
    """
    )

    cr.execute("DELETE FROM ir_translation WHERE type IN ('selection', 'constraint', 'sql_constraint')")
    cr.execute("DROP INDEX IF EXISTS ir_translation_selection_unique")
