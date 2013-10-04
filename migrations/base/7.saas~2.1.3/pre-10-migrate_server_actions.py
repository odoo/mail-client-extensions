# -*- coding: utf-8 -*-
import re
from functools import partial
from openerp.addons.base.maintenance.migrations import util

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

    # email actions are defined by email_template module
    cr.execute("SELECT id, email, subject, message, model_id FROM ir_act_server WHERE state=%s", ('email',))
    email_actions = list(cr.fetchall())
    if not email_actions:
        return

    util.create_column(cr, 'ir_act_server', 'template_id', 'int4')

    util.force_install_module(cr, 'email_template')
    if not util.table_exists(cr, 'email_template'):
        cr.execute("""CREATE TABLE email_template(
                        id SERIAL NOT NULL,
                        model_id integer,
                        subject varchar,
                        email_from varchar,
                        email_to varchar,
                        body_html varchar,
                      PRIMARY KEY(id))""")

    email_from = '${user.email}'
    to_jinja = partial(re.sub, r'(\[\[.+\]\])', r'${\1}')

    for aid, email_to, subject, message, model_id in email_actions:

        email_to = (email_to or '""').strip() or '""'
        if email_to[0] == "[" and email_to[-1] == "]":
            email_to = "${',',join(%s)}" % (email_to,)
        else:
            email_to = "${%s}" % (email_to,)

        cr.execute("""INSERT INTO email_template(model_id, subject, email_from, email_to, body_html)
                                          VALUES(%s, %s, %s, %s, %s)
                      RETURNING id
                   """, (model_id, to_jinja(subject), email_from, email_to, to_jinja(message)))

        tpl_id, = cr.fetchone()
        cr.execute("UPDATE ir_act_server SET template_id=%s WHERE id=%s", (tpl_id, aid))
