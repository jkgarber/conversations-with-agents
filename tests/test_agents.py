import pytest
from incontext.db import get_db


def test_index(client, auth):
    # user must be logged in
    response = client.get('/agents/', follow_redirects=True) # when not logged in each page shows links to log in or register. 
    assert b'Log In' in response.data
    assert b'Register' in response.data
    
    # serve the agents overview page to logged-in user
    auth.login()
    response = client.get('/agents/') # the index view should display information about the agent that was added with the test data.
    # base nav
    assert b'Log Out' in response.data # when logged in there's a ling to log out.
    # main
    assert b'gpt-4.1-mini' in response.data
    assert b'Test' in response.data
    assert b'Testing Agent' in response.data
    assert b'Created: 01.01.2025' in response.data
    assert b'Creator: test' in response.data
    assert b'Reply with one word: &#34;Working&#34;.' in response.data
    assert b'href="/agents/1/update"' in response.data
    assert b'href="/conversations/1"' in response.data


def test_creator_only_access(client, auth, app):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE agents SET creator_id = 3 where id = 1')
        db.commit()
    auth.login()
    response = client.get('/agents/')
    assert b'gpt-4.1-mini' not in response.data
    assert b'Testing Agent' not in response.data
    assert b'href="agents/1/update"' not in response.data


@pytest.mark.parametrize('path', (
    'agents/create',
    'agents/1/update',
    'agents/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == '/auth/login'


def test_creator_required(app, client, auth):
    # change the agent creator to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE agents SET creator_id = 3 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify another user's agent 
    assert client.post('agents/1/update').status_code == 403
    assert client.post('agents/1/delete').status_code == 403
    # current user doesn't see Edit link
    assert b'href="/agents/1/update"' not in client.get('/agents').data


@pytest.mark.parametrize('path', (
    'agents/2/update',
    'agents/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('agents/create').status_code == 200

    response = client.post('agents/create', data={'model': 'gpt-4.1-mini', 'name': 'Test 1', 'role': 'Testing Agent', 'instructions': 'Reply with one word: "Working".'})
    response = client.post('agents/create', data={'model': 'claude-3-5-haiku-latest', 'name': 'Test 2', 'role': 'Testing Agent', 'instructions': 'Reply with one word: "Working".'})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM agents').fetchone()[0]
        assert count == 3
    

def test_update(client, auth, app):
    auth.login()
    assert client.get('agents/1/update').status_code == 200
    
    client.post('/agents/1/update', data={'model': 'gpt-4.1', 'name': 'Test 1', 'role': 'Testing Agent', 'instructions': 'Reply with one word: "Working".'})
    with app.app_context():
        db = get_db()
        agent = db.execute('SELECT * FROM agents WHERE id = 1').fetchone()
        assert agent['model'] == 'gpt-4.1'
        assert agent['name'] == 'Test 1'
        assert agent['role'] == 'Testing Agent'
        assert agent['instructions'] == 'Reply with one word: "Working".'
    
    client.post('/agents/1/update', data={'vendor': 'anthropic', 'model': 'claude-3-5-haiku-latest', 'name': 'Test 1', 'role': 'Testing Agent', 'instructions': 'Reply with one word: "Working".'})
    with app.app_context():
        db = get_db()
        agent = db.execute('SELECT * FROM agents WHERE id = 1').fetchone()
        assert agent['vendor'] == 'anthropic'
        assert agent['model'] == 'claude-3-5-haiku-latest'
        assert agent['name'] == 'Test 1'
        assert agent['role'] == 'Testing Agent'
        assert agent['instructions'] == 'Reply with one word: "Working".'


@pytest.mark.parametrize('path', (
    '/agents/create',
    '/agents/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'model': '', 'name': 'Test', 'role': 'Test Agent', 'instructions': 'Reply with one word: "Working".'})
    assert b'Model, name, role, and instructions are all required.' in response.data
    
    response = client.post(path, data={'model': 'gpt-4.1', 'name': '', 'role': 'Test Agent', 'instructions': 'Reply with one word: "Working".'})
    assert b'Model, name, role, and instructions are all required.' in response.data

    response = client.post(path, data={'model': 'gpt-4.1', 'name': 'Test', 'role': '', 'instructions': 'Reply with one word: "Working".'})
    assert b'Model, name, role, and instructions are all required.' in response.data

    response = client.post(path, data={'model': 'gpt-4.1', 'name': 'Test', 'role': 'Test Agent', 'instructions': ''})
    assert b'Model, name, role, and instructions are all required.' in response.data


def test_delete(client, auth, app):
    # the agent is still related to a conversation. app should flash an error.
    auth.login()
    response = client.post('/agents/1/delete', follow_redirects=True)
    assert b'Cannot delete this agent as it is linked to 1 conversation(s).' in response.data
    
    # delete the related conversations and then the delete view should should redirect to the index url and the agent should no longer exist in the db.
    client.post('conversations/1/delete') 
    response = client.post('/agents/1/delete')
    assert response.headers['Location'] == '/agents/'
    with app.app_context():
        db = get_db()
        agent = db.execute('SELECT * FROM agents WHERE id = 1').fetchone()
        assert agent is None
        count = db.execute('SELECT COUNT(id) from conversation_agent_relations WHERE agent_id = 1').fetchone()[0]
        assert count == 0


