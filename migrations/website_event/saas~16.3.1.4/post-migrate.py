# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO event_question(
            event_id, sequence, create_uid, write_uid, question_type, title,
            once_per_order, is_mandatory_answer, create_date, write_date)
        SELECT
            e.id, 0, e.create_uid, e.write_uid, v.name, jsonb_build_object('en_US', initcap(v.name)),
            False, v.mandatory, NOW(), NOW()
        FROM event_event e
        JOIN (values ('name', True), ('email', True), ('phone', False)) as v(name, mandatory) on true
    """
    )

    cr.execute(
        """
        INSERT INTO event_question(
            event_type_id, sequence, create_uid, write_uid, question_type, title,
            once_per_order, is_mandatory_answer, create_date, write_date)
        SELECT
            e.id, 0, e.create_uid, e.write_uid, v.name, jsonb_build_object('en_US', initcap(v.name)),
            False, v.mandatory, NOW(), NOW()
        FROM event_type e
        JOIN (values ('name', True), ('email', True), ('phone', False)) as v(name, mandatory) on true
    """
    )
