from odoo.upgrade import util


def migrate(cr, version):
    todo_type = util.ref(cr, "mail.mail_activity_data_todo")
    query = cr.mogrify(
        """
            UPDATE mail_activity a
               SET activity_type_id = %s
              FROM mail_activity_type t
             WHERE t.id = a.activity_type_id
               AND t.category = 'grant_approval'
        """,
        [todo_type],
    ).decode()
    util.explode_execute(cr, query, table="mail_activity", alias="a")

    util.remove_record(cr, "web_studio.mail_activity_data_approve")
    cr.execute("SELECT id from mail_activity_type WHERE category = 'grant_approval'")
    if cr.rowcount:
        util.remove_records(cr, "mail.activity.type", [tid for (tid,) in cr.fetchall()])

    util.create_column(cr, "mail_activity", "studio_approval_request_id", "int4")
    query = """
        UPDATE mail_activity a
           SET studio_approval_request_id = r.id
          FROM studio_approval_request r
         WHERE r.mail_activity_id = a.id
    """
    util.explode_execute(cr, query, table="mail_activity", alias="a")
