# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        return

    # Copy survey_response (old) to survey_user_input (new)
    util.create_column(cr, 'survey_user_input','old_response_id','integer')

    cr.execute("""select r.survey_id, r.date_create, r.response_type, r.state, u.partner_id, r.id, r.create_uid, r.create_date, r.write_date, r.write_uid
                from survey_response r, res_users u where r.user_id = u.id""")
    new_inputs = cr.dictfetchall()
    import uuid
    for input in new_inputs:
        token = str(uuid.uuid4())
        cr.execute("""insert into survey_user_input(survey_id, date_create, type, state, partner_id, token, old_response_id, create_uid, create_date, write_date, write_uid)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    [input['survey_id'], input['date_create'], input['response_type'], input['state'], input['partner_id'], token, input['id'], input['create_uid'], input['create_date'], input['write_date'], input['write_uid'],])
