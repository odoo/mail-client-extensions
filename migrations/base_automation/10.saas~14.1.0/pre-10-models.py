# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = util.splitlines("""
        ir_cron_{crm_action,data_base_automation_check}

        access_base_{action_rule,automation}
        access_base_{action_rule,automation}_config
        access_base_{action_rule,automation}_lead_test
        access_base_{action_rule,automation}_line_test

        view_base_{action_rule,automation}_form
        view_base_{action_rule,automation}_tree

        base_{action_rule,automation}_act
        menu_base_{action_rule,automation}_form

        # demo server.action merged as _inherits
        test_{action,rule_recursive_ir_actions_server}
        test_{action_context,rule_on_write_check_context_ir_actions_server}
    """)
    for rename in renames:
        util.rename_xmlid(cr, *util.expand_braces('base_automation.' + rename))

    # model changes
    util.rename_field(cr, 'base.action.rule', 'kind', 'trigger')
    util.rename_model(cr, 'base.action.rule', 'base.automation')

    util.create_column(cr, 'base_automation', 'action_server_id', 'int4')

    # create/link action server to action rule

    AUTO = '# Automatically created by migration.'
    IAS = util.env(cr)['ir.actions.server']

    cr.execute("""
        SELECT bar.id, bar.name, bar.model_id, bar.sequence, bar.act_user_id,
               array_remove(array_agg(sa.ir_act_server_id), NULL),
               array_remove(array_agg(p.res_partner_id), NULL)
          FROM base_automation bar
     LEFT JOIN base_action_rule_ir_act_server_rel sa ON (sa.base_action_rule_id = bar.id)
     LEFT JOIN base_action_rule_res_partner_rel p ON (p.base_action_rule_id = bar.id)
      GROUP BY bar.id, bar.name, bar.model_id, bar.act_user_id
      ORDER BY bar.id
    """)

    for bar_id, bar_name, bar_model_id, bar_seq, set_user_id, action_ids, partner_ids in cr.fetchall():
        act_set_user = act_set_followers = ""
        if set_user_id:
            act_set_user = "records.write({'user_id': %d})\n" % (set_user_id,)
        if partner_ids:
            act_set_followers = "records.message_subscribe(%r)\n" % (partner_ids,)

        as_id = None
        if not action_ids and not set_user_id and partner_ids:
            # special case: only set followers
            as_id = IAS.create({
                'name': bar_name,
                'model_id': bar_model_id,
                'state': 'multi',
                'partner_ids': [(6, 0, partner_ids)],
            }).id
            # In v11 [1], There is a @constrains() that check we only set followers on mail.thread.
            # However, as we are in `mail` module, models does not already have the flag set,
            # raising a ValidationError. Bypass the check via SQL...
            # [1] https://github.com/odoo/odoo/commit/c7d1466996dd2eca1776e390f9da9595317a4329
            cr.execute("UPDATE ir_act_server SET state='followers' WHERE id=%s", [as_id])
        elif len(action_ids) != 1:
            ret = ''
            if action_ids:
                ret = "action = env['ir.actions.server'].browse(%r).run()" % (action_ids,)

            as_id = IAS.create({
                'name': bar_name,
                'model_id': bar_model_id,
                'state': 'code',
                'code': '%s\n\n%s%s%s' % (AUTO, act_set_user, act_set_followers, ret),
            }).id
        else:
            action = IAS.browse(action_ids[0])
            if act_set_user or act_set_followers:
                if action.state != 'code':
                    code = "action = env['ir.actions.server'].browse(%d).run()" % (action.id,)
                else:
                    code = action.code

                as_id = action.copy({
                    'name': bar_name,
                    'model_id': bar_model_id,
                    'state': 'code',
                    'code': '%s\n\n%s%s\n\n%s' % (AUTO, act_set_user, act_set_followers, code),
                    # 'base_automation' has not been added yet since module is not loaded yet
                    'usage': 'ir_actions_server',
                }).id
            else:
                # XXX update action name with `bar_name`?
                as_id = action.id

        # set correct usage for action server (can't do it using ORM as module is not loaded yet)
        cr.execute("UPDATE ir_act_server SET usage='base_automation', sequence=%s WHERE id=%s",
                   [bar_seq, as_id])
        # and link base.automation to the action server
        cr.execute("UPDATE base_automation SET action_server_id=%s WHERE id=%s", [as_id, bar_id])

    IAS.clear_caches()

    # remove old m2m
    cr.execute("DROP TABLE base_action_rule_ir_act_server_rel")
    cr.execute("DROP TABLE base_action_rule_res_partner_rel")

    for f in 'act_user_id act_followers server_action_ids'.split():
        util.remove_field(cr, 'base.automation', f)
    util.remove_column(cr, 'base_automation', 'name')   # keep ir.model.fields
