# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    for a in 'actions report.xml act_window act_window_close act_url client'.split():
        util.remove_field(cr, 'ir.actions.' + a, 'usage')

    # `usage` column is an inherited one (postgres side)
    # So, deleting it from ir.actions.actions actually delete it from other model
    # We need to recreate it.
    util.create_column(cr, 'ir_act_server', 'usage', 'varchar')

    cr.execute("DELETE FROM ir_act_server WHERE state='trigger'")

    # related field `model_name` is now stored
    util.create_column(cr, 'ir_act_server', 'model_name', 'varchar')
    cr.execute("""
        UPDATE ir_act_server s
           SET usage = 'ir_actions_server',
               model_name = m.model
          FROM ir_model m
         WHERE m.id = s.model_id
    """)

    # prepare "write" action "code" column
    cr.execute("""
        UPDATE ir_act_server
           SET code =
'# Automatically converted by migration
'   -- trailing CR is important
         WHERE state = 'object_write'
           AND use_write IN ('other', 'expression')
    """)
    # redefine deprecated variables if used...
    renames = {
        'obj': 'record',
        'object': 'record',
        'context': 'dict(env.context)',     # create a writeable version
        'user': 'env.user',
        'cr': 'env.cr',
    }
    for f, t in renames.items():
        assignment = '%s = %s\n' % (f, t)
        match = r'\y%s\y' % (f,)
        cr.execute("""
            UPDATE ir_act_server
               SET code= %s || code
             WHERE code ~ %s
               AND state = 'code'
        """, [assignment, match])
        cr.execute("""
            UPDATE ir_act_server
               SET code= code || %s
             WHERE write_expression ~ %s
               AND state = 'object_write'
               AND use_write = 'expression'
        """, [assignment, match])

    # inject condition in code
    cr.execute("""
        UPDATE ir_act_server
           SET code=
'if ' || condition || ':
    return
' || code
         WHERE COALESCE(condition, 'True') != 'True'
           AND state='code'
    """)

    # Convert "client_action" action to code ones
    cr.execute("""
        UPDATE ir_act_server s
           SET state='code',
               code='action = self.env["' || a.type || '"].browse(' || a.id || ').read()[0]'
          FROM ir_actions a
         WHERE a.id = s.action_id
           AND s.state = 'client_action'
    """)

    # adapt "create" actions
    cr.execute("UPDATE ir_act_server SET link_field_id=NULL WHERE NOT link_new_record")
    cr.execute("""
        UPDATE ir_act_server
           SET crud_model_id = model_id
         WHERE state='object_create'
           AND use_create = 'new'
    """)
    cr.execute("""
        UPDATE ir_act_server
           SET state = 'code',
               code = '# Automatically converted by migration
eval_context = dict(env=env, model=model, record=record, records=records,
                    object=record, obj=record, user=env.user, context=dict(env.context))
self = env["ir.actions.server"].browse(' || id || ')
data = {}
for exp in self.fields_lines:
    data[exp.col1.name] = exp.eval_value(eval_context=eval_context)[exp.id]

' ||
CASE WHEN use_create = 'copy_current' THEN
    'record = env[self.model_id.model].browse(env.context.get("active_id"))'
ELSE
    'record = env["' || split_part(ref_object, ',', 1) || '"].browse(' || split_part(ref_object, ',', 2) || ')'
END
|| '
rec = record.copy(data)

if self.link_field_id:
    record.write({self.link_field_id.name: rec.id})
'
         WHERE state = 'object_create'
           AND use_create IN ('copy_current', 'copy_other')
    """)

    # adapt "write" action on other model or using an expression
    cr.execute("""
        UPDATE ir_act_server
           SET state = 'code',
               code = code || '
eval_context = dict(env=env, model=model, record=record, records=records,
                    object=record, obj=record, user=env.user, context=dict(env.context))
object = obj = record
user = env.user
context = dict(env.context)
self = env["ir.actions.server"].browse(' || id || ')
data = {}
for exp in self.fields_lines:
    data[exp.col1.name] = exp.eval_value(eval_context=eval_context)[exp.id]

' ||
CASE WHEN use_write = 'other' THEN
    'ref_id = ' || split_part(ref_object, ',', 2)
ELSE
    'ref_id = int(' || COALESCE(write_expression, '0') || ')'
END
|| '
env[self.model_id.model].browse(ref_id).write(data)

'
         WHERE state = 'object_write'
           AND use_write IN ('other', 'expression')
    """)

    # cleanup
    oldfields = """
        action_id
        conditional
        use_relational_model wkf_transition_id wkf_model_id wkf_model_name wkf_field_id
        use_create ref_object link_new_record use_write write_expression
        model_object_field sub_object sub_model_object_field copyvalue id_object id_value
        crud_model_name
    """.split()
    for f in oldfields:
        util.remove_field(cr, 'ir.actions.server', f)
