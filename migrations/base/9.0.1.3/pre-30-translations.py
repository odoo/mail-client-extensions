# -*- coding: utf-8 -*-
import re
from openerp.addons.base.maintenance.migrations import util
from openerp.tools.translate import xml_translate

def migrate(cr, version):
    arch_column = 'arch_db' if util.column_exists(cr, 'ir_ui_view', 'arch_db') else 'arch'
    # convert 'field', 'help', 'view' into 'model'
    cr.execute("""
        UPDATE ir_translation t
           SET type='model',
               name='ir.model.fields,field_description',
               res_id=f.id
          FROM ir_model_fields f
         WHERE f.model = split_part(t.name, ',', 1)
           AND f.name = split_part(t.name, ',', 2)
           AND t.type = 'field'
    """)
    cr.execute("""
        UPDATE ir_translation t
           SET type='model',
               name='ir.model.fields,help',
               res_id=f.id
          FROM ir_model_fields f
         WHERE f.model = split_part(t.name, ',', 1)
           AND f.name = split_part(t.name, ',', 2)
           AND t.type = 'help'
    """)

    # qweb translations
    cr.execute("""
        UPDATE ir_translation t
           SET type='model',
               name='ir.ui.view,arch_db'
         WHERE type='view'
           AND name='website'
           AND COALESCE(res_id, 0) != 0
     RETURNING res_id
    """)

    view_ids = set(v[0] for v in cr.fetchall())
    if view_ids:
        cr.execute("""
            SELECT lang
              FROM ir_translation
             WHERE type='model'
               AND name='ir.ui.view,arch_db'
          GROUP BY lang
        """)
        langs = [l[0] for l in cr.fetchall()]

        def search(trans, view_ids, lang):
            cr.execute("""
                SELECT value, res_id
                  FROM ir_translation
                 WHERE name='ir.ui.view,arch_db'
                   AND type='model'
                   AND res_id = ANY(%s)
                   AND src=%s
                   AND lang=%s
                   AND value IS NOT NULL
              -- favor inherit views before primary one: goes up hierarchy
              -- would use `array_position` in pg 9.5
              ORDER BY strpos(array_to_string(%s, ',') || ',', res_id || ',') DESC
            """, [view_ids, trans, lang, view_ids])
            if not cr.rowcount:
                return trans, None
            return cr.fetchone()

        # in 8.0, translation where linked to the root view
        # in 9.0, each inherited view own its translations
        cr.execute("""
            WITH RECURSIVE view_tree AS (
                SELECT id, ARRAY[id] as path FROM ir_ui_view WHERE id IN %s
                UNION
                SELECT v.id, t.path || v.id as path FROM ir_ui_view v JOIN view_tree t ON (v.inherit_id = t.id)
            )
            SELECT v.id, t.path, v.{0} FROM ir_ui_view v JOIN view_tree t ON (v.id = t.id)

        """.format(arch_column), [tuple(view_ids)])
        for view, view_path, arch in cr.fetchall():
            def cb(term):
                for lang in langs:
                    match, res_id = search(term, view_path, lang)
                    if match != term and res_id == view:
                        # already translated, skip
                        continue
                    trans = term
                    # in 8.0, translation of qweb view was done by splitting on each tag.
                    # This is not the case anymore in 9.0.
                    # We need to recompose the translation by splitting tags ourself.
                    tag_split = "</?\w+[^>]*>"      # "<br\s*/?>"
                    for line in sorted(re.split(tag_split, term), key=len, reverse=True):
                        line = line.strip()
                        if not line:
                            continue
                        trans = trans.replace(line, search(line, view_path, lang)[0], 1)
                    if trans != term:
                        cr.execute("""
                            INSERT INTO ir_translation(lang, src, name, res_id, state, value, type)
                            VALUES (%s, %s, 'ir.ui.view,arch_db', %s, 'translated', %s, 'model')
                        """, [lang, term, view, trans])

            xml_translate(cb, arch)

    # copy non-qweb view translations for each matching view
    columns = util.get_columns(cr, 'ir_translation', ('id', 'type', 'name', 'res_id'))
    t_columns = ["t." + c for c in columns]
    cr.execute("""INSERT INTO ir_translation(name, type, res_id, {columns})
                       SELECT 'ir.ui.view,arch_db', 'model', v.id, {t_columns}
                         FROM ir_translation t
                         JOIN ir_ui_view v ON (v.model = t.name AND strpos(v.{arch_column}, t.src) != 0)
                        WHERE t.type = 'view'
                          AND COALESCE(t.res_id, 0) = 0
               """.format(columns=', '.join(columns), t_columns=', '.join(t_columns), arch_column=arch_column))

    # remove deprecated (and unreachable) translations
    cr.execute("""
        DELETE
          FROM ir_translation
         WHERE type IN ('rml', 'xsl',
                        'wizard_button', 'wizard_field', 'wizard_view',
                        'field', 'help', 'view')
    """)
