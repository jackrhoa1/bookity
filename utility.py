from difflib import SequenceMatcher
import flask_sqlalchemy

# compares similarity of authors
def compare_authors(s1, s2):
    __res = SequenceMatcher(None, s1, s2).ratio()
    return __res

def reset_table(table: flask_sqlalchemy.model.DefaultMeta, db, app):
    with app.app_context():
        table.__table__.drop(db.engine)
        db.create_all()
