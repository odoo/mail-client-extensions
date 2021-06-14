# -*- coding: utf-8 -*-


def migrate(cr, version):
    """
        Due to the new ORM-pocalypse, the values passed to `.write()` now goes through the cache, which validates the value.
        For date and datetime, it only accepts ISO dates.
        In previous versions, the value was directly send to PostgreSQL and take advantage of the coercion of strings to date and
        timestamps. However, there are some values that were valid in PostgreSQL, that aren't anymore in the python version.

    [local] chs@t=# select 'today'::date;
    ┌────────────┐
    │    date    │
    ├────────────┤
    │ 2021-06-11 │
    └────────────┘
    (1 row)

    Time: 0.189 ms
    [local] chs@t=# select 'today'::timestamp;
    ┌─────────────────────┐
    │      timestamp      │
    ├─────────────────────┤
    │ 2021-06-11 00:00:00 │
    └─────────────────────┘
    (1 row)

    Time: 0.188 ms
    [local] chs@t=# select 'now'::date;
    ┌────────────┐
    │    date    │
    ├────────────┤
    │ 2021-06-11 │
    └────────────┘
    (1 row)

    Time: 0.175 ms
    [local] chs@t=# select 'now'::timestamp;
    ┌────────────────────────────┐
    │         timestamp          │
    ├────────────────────────────┤
    │ 2021-06-11 10:27:14.383917 │
    └────────────────────────────┘
    (1 row)

    Time: 0.175 ms
    [local] chs@t=# select '    today      (       )  '::timestamp;
    ┌─────────────────────┐
    │      timestamp      │
    ├─────────────────────┤
    │ 2021-06-11 00:00:00 │
    └─────────────────────┘
    (1 row)

    Time: 0.164 ms
    [local] chs@t=# select 'yesterday'::date;
    ┌────────────┐
    │    date    │
    ├────────────┤
    │ 2021-06-10 │
    └────────────┘
    (1 row)

    Time: 0.247 ms
    [local] chs@t=# select 'tomorrow'::date;
    ┌────────────┐
    │    date    │
    ├────────────┤
    │ 2021-06-12 │
    └────────────┘
    (1 row)

    Time: 0.138 ms
    """

    matches = [
        # (ttype, regex, replacement)
        ("date", r"^\s*(?:today|now)\s*(?:\(\s*\))?\s*$", "datetime.date.today()"),
        ("date", r"^\s*yesterday\s*(?:\(\s*\))?\s*$", "datetime.date.today() - datetime.timedelta(days=1"),
        ("date", r"^\s*tomorrow\s*(?:\(\s*\))?\s*$", "datetime.date.today() + datetime.timedelta(days=1"),
        ("datetime", r"^\s*(?:today|now)\s*(?:\(\s*\))?\s*$", "datetime.datetime.today()"),
    ]

    for ttype, regex, replacement in matches:
        cr.execute(
            """
                UPDATE ir_server_object_lines l
                   SET evaluation_type = 'equation',
                       value = %s
                  FROM ir_model_fields f
                 WHERE f.id = l.col1
                   AND f.ttype = %s
                   AND l.value ~* %s
            """,
            [replacement, ttype, regex],
        )
