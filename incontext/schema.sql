DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS conversation_agent_relations;

CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL
);

CREATE TABLE conversations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	creator_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name TEXT NOT NULL,
	FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE messages (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	conversation_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	content TEXT NOT NULL,
	human INTEGER NOT NULL,
	FOREIGN KEY (conversation_id) REFERENCES conversations (id)
);

CREATE TABLE agents (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	creator_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	model TEXT NOT NULL,
	name TEXT NOT NULL,
	role TEXT NOT NULL,
	instructions TEXT NOT NULL,
	vendor TEXT NOT NULL,
	FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE conversation_agent_relations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	conversation_id INTEGER NOT NULL,
	agent_id INTEGER NOT NULL,
	FOREIGN KEY (conversation_id) REFERENCES conversations (id),
	FOREIGN KEY (agent_id) REFERENCES agents (id)
);
