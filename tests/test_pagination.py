from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import cast

import flask_sqlalchemy as fsa


def test_basic_pagination():
    p = fsa.Pagination(None, 1, 20, 500, [])
    assert p.page == 1
    assert not p.has_prev
    assert p.has_next
    assert p.total == 500
    assert p.pages == 25
    assert p.next_num == 2
    assert list(p.iter_pages()) == [1, 2, 3, 4, 5, None, 24, 25]
    p.page = 10
    assert list(p.iter_pages()) == [1, 2, None, 8, 9, 10, 11, 12, 13, 14, None, 24, 25]


def test_pagination_pages_when_0_items_per_page():
    p = fsa.Pagination(None, 1, 0, 500, [])
    assert p.pages == 0


def _create_todo_entries(Todo, app, db):
    with app.app_context():
        db.session.add_all([Todo('', '') for _ in range(100)])
        db.session.commit()


def test_query_paginate(app, db, Todo):
    _create_todo_entries(Todo, app, db)

    @app.route('/')
    def index():
        p = Todo.query.paginate()
        return '{0} items retrieved'.format(len(p.items))

    c = app.test_client()
    # request default
    r = c.get('/')
    assert r.status_code == 200
    # request args
    r = c.get('/?per_page=10')
    assert r.data.decode('utf8') == '10 items retrieved'

    with app.app_context():
        # query default
        p = Todo.query.paginate()
        assert p.total == 100


def test_allows_passing_in_an_object_that_responds_to_count_with_the_current_object(app, db, Todo):
    _create_todo_entries(Todo, app, db)

    def counter(model):
        return 4  # statistical average ;)

    p = Todo.query.paginate(counter=counter)

    assert p.total == 4, 'expected to have returned our fixed count'
