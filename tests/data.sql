INSERT INTO users (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO conversations (name, creator_id, created)
VALUES
	('test name', 2, '2025-01-01 00:00:00');			

INSERT INTO messages (conversation_id, content, human)
VALUES
	(1, 'This is a test.', 1),
	(1, 'Working', 0),
	(1, 'This is a test.', 1);

INSERT INTO agents (model, name, role, instructions, creator_id, created)
VALUES
	('gpt-4.1-mini', 'Test', 'Testing Agent', 'Reply with one word: "Working".', 2, '2025-01-01 00:00:00');

INSERT INTO conversation_agent_relations (conversation_id, agent_id)
VALUES
	(1, 1);
