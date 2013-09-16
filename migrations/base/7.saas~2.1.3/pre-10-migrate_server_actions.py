def migrate(cr, v):
    cr.execute('DELETE from ir_act_server where state=%s', ('sms',))

    # convert "loop" actions
    cr.execute("""UPDATE ir_act_server
                     SET state=%s,
                         code='expr = eval(str("' || replace(expression, '"', '\"') || '"))' || E'\n' ||
                              'ias = pool["ir.actions.server"]' || E'\n' ||
                              'for i in expr:' || E'\n' ||
                              '    context["active_id"] = i.id' || E'\n' ||
                              '    ias.run(cr, uid, [' || loop_action || '], context)'
                   WHERE state=%s
                     AND loop_action IS NOT NULL
                     AND expression IS NOT NULL
               """, ('code', 'loop'))

    # remove left ones
    cr.execute('DELETE from ir_act_server where state=%s', ('loop',))
