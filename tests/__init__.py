import os
import app as flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    # test empty database
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    # helper function to add an entry
    def add_messages(self, app, title, category, text):
        return self.app.post('/add', data=dict(
            title=title,
            category=category,
            text=text
        ), follow_redirects=True)

    # test adding messages
    def test_add_messages(self):
        rv = self.add_messages(self.app, '<Hello>', 'Test', '<strong>HTML</strong> allowed here')
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'Test' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    # test edit view
    def test_edit_messages(self):
        self.add_messages(self.app, '<Hello>', 'Test', '<strong>HTML</strong> allowed here')
        rv = self.app.get('/edit?id=1', follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'Test' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    # test edit view if id is invalid
    def test_edit_messages_invalid_id(self):
        self.add_messages(self.app, '<Hello>', 'Test', '<strong>HTML</strong> allowed here')
        rv = self.app.get('/edit?id=2', follow_redirects=True)
        assert b'Entry not found' in rv.data

    # test updating messages in edit view
    def test_update_messages(self):
        self.add_messages(self.app, '<Hello>', 'Test', '<strong>HTML</strong> allowed here')
        self.app.get('/edit?id=1', follow_redirects=True)
        rv = self.app.post('/update', data=dict(
            title='<Edit Title>',
            category='Edit Category',
            text='Edit Text',
            id=1,
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Edit Title&gt;' in rv.data
        assert b'Edit Category' in rv.data
        assert b'Edit Text' in rv.data

    # test deleting messages
    def test_delete_messages(self):
        self.add_messages(self.app, '<Hello>', 'Test', '<strong>HTML</strong> allowed here')
        rv = self.app.post('/delete', data=dict(id=1), follow_redirects=True)
        assert b'No entries here so far' in rv.data
        assert b'&lt;Edit Title&gt;' not in rv.data
        assert b'Edit Category' not in rv.data
        assert b'Edit Text' not in rv.data


if __name__ == '__main__':
    unittest.main()
