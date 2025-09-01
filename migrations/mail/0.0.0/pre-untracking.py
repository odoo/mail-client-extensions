"""
Historically tracking could get copied onto related fields even when that made
no sense (it rarely did). Remove tracking attribute if that's an option.
"""


def migrate(cr, version):
    cr.execute("""
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = 'ir_model_fields'
           AND column_name = 'tracking'
    """)
    if not cr.rowcount:
        return

    cr.execute("""
        UPDATE ir_model_fields f
           SET tracking = NULL
          FROM ir_model m
         WHERE m.id = f.model_id
           AND f.tracking IS NOT NULL
           AND (   NOT coalesce(f.store, false)
                OR NOT coalesce(m.is_mail_thread, false))
    """)
