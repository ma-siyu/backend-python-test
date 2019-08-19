DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS todos;
CREATE TABLE todos (
  id INTEGER PRIMARY KEY,
  user_id INT(11) NOT NULL,
  description VARCHAR(255) NOT NULL,
  todo_status INT(1) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (username, password) VALUES
('user1', 'user1'),
('user2', 'user2'),
('user3', 'user3');

INSERT INTO todos (user_id, description, todo_status) VALUES
(1, 'Vivamus tempus', 0),
(1, 'lorem ac odio', 0),
(1, 'Ut congue odio', 0),
(1, 'Sodales finibus', 0),
(1, 'Accumsan nunc vitae', 0),
(2, 'Lorem ipsum', 0),
(2, 'In lacinia est', 0),
(2, 'Odio varius gravida', 0);
