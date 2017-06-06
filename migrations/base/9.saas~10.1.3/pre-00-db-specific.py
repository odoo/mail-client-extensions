# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.force_noupdate(cr, 'openerp_website.odoo_blog_sidebar_blogs', False)
    util.remove_view(cr, view_id=8816)      # custom inherited view now builtin
    util.remove_view(cr, view_id=8978)      # please define xmlids when creating views manually...

def _db_natural_fresh(cr, version):
    cr.execute("DELETE FROM ir_model_fields WHERE id=5754")
    cr.execute("select id from ir_ui_view where arch_db like '%x\_claim\_ids%'")
    for vid, in cr.fetchall():
        util.remove_view(cr, view_id=vid)

def _boldom(cr, version):
    cr.execute('''UPDATE ir_ui_view SET inherit_id=NULL,mode='primary',model='helpdesk.ticket',name='[MIG] CRM Claims form' WHERE id=604;''')
    cr.execute('''delete from ir_config_parameter where key='mail.bounce.alias';''')
    cr.execute("DELETE FROM ir_server_object_lines WHERE id=403")
    cr.execute("UPDATE ir_ui_view SET arch_db=%s WHERE id=837",
               ["""<xpath expr="//field[@name='fax']/.."><group/></xpath>"""])

def _megamanhk(cr, version):
    # migration of custom fields from crm_claim to project_issue
    cr.execute('''SELECT id
                    FROM ir_model
                   WHERE model='project.issue' ''')
    model_project_issue_id = cr.fetchone()[0]

    cr.execute('''UPDATE crm_claim SET create_date=date;''')

    util.create_column(cr, 'project_issue', 'ref', 'varchar')
    cr.execute('''
    INSERT INTO ir_model_fields(model, model_id, name, field_description, ttype, state, store, copy, selection)
    VALUES ('project.issue',
            %d,
            'ref',
            'Reference',
            'reference',
            'manual',
            TRUE,
            TRUE,
            '((''res.partner'',''Partner''),(''product.product'',''Product''),(''account.invoice'',''Invoice''),(''account.voucher'',''Voucher''),(''sale.order'',''Sales Order''))');
    ''' % model_project_issue_id)

    util.create_column(cr, 'project_issue', 'x_claim_no', 'varchar')
    util.create_column(cr, 'project_issue', 'x_old_ref_no', 'varchar')
    util.create_column(cr, 'project_issue', 'x_Lot', 'varchar')
    util.create_column(cr, 'project_issue', 'x_Voltage_Supplied', 'varchar')
    util.create_column(cr, 'project_issue', 'x_Install_Height', 'varchar')
    util.create_column(cr, 'project_issue', 'x_Supply_Condition', 'varchar')
    util.create_column(cr, 'project_issue', 'x_Duty_Cycle', 'varchar')
    util.create_column(cr, 'project_issue', 'x_Ambient_Temp', 'int4')
    util.create_column(cr, 'project_issue', 'x_QtyInstalled', 'int4')
    util.create_column(cr, 'project_issue', 'x_QtyFailed', 'int4')
    util.create_column(cr, 'project_issue', 'x_Worked_Hours', 'int4')
    util.create_column(cr, 'project_issue', 'x_Install_Date', 'date')
    cr.execute('''
        INSERT INTO ir_model_fields(model, model_id, name, field_description, ttype, state, translate, readonly, selectable, required, store)
        SELECT 'project.issue',
               %d,
               name,
               field_description,
               ttype,
               state,
               translate,
               readonly,
               selectable,
               required,
               store
          FROM ir_model_fields
         WHERE model='crm.claim' AND state='manual' AND ttype!='many2many'; ''' % model_project_issue_id)

    # migrate old crm_claim tags to project_tags
    cr.execute('''
        INSERT INTO project_tags(create_uid,create_date,write_uid,write_date,name)
        SELECT create_uid,
               create_date,
               write_uid,
               write_date,
               x_name
        FROM x_claim_tag
        ON CONFLICT ON CONSTRAINT project_tags_name_uniq DO NOTHING;
        ''')
    cr.execute('''CREATE TABLE _tmp_claim_tag(
        claim_no varchar,
        tag_name varchar);
        ''')
    cr.execute('''INSERT INTO _tmp_claim_tag
                  SELECT c.x_claim_no,
                         t.x_name
                  FROM crm_claim c
                  JOIN x_x_claim_tag_crm_claim_x_tags_rel r ON r.id1 = c.id
                  JOIN x_claim_tag t ON t.id = r.id2; ''')

    # migration of custom BAR from crm_claim to project_issue
    cr.execute('''UPDATE base_action_rule
                     SET model_id=%d
                   WHERE model_id=(SELECT id
                                     FROM ir_model
                                    WHERE model='crm.claim')''' % model_project_issue_id)
    cr.execute('''UPDATE ir_act_server
                     SET model_id=%d,
                         code='
sq_number = env[''ir.sequence''].next_by_code(''crm.claim'')
if sq_number:
    object.write({''x_claim_no'': sq_number})
'
                   WHERE id=384''' % model_project_issue_id)


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
        '676796d7-881a-42c1-b5c8-ecae4452ec23': _db_natural_fresh,
        '39b15f26-b737-4420-94bb-156191526fbf': _boldom,
        '16a70f1b-893a-4411-aa2a-d939171fac7d': _megamanhk,
    })
