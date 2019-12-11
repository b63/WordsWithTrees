-- insert sapling tree with only a trunk
INSERT INTO tree (tree_id, tree_name, full_width, full_height) VALUES (5, 'sapling', 1024, 1024);

-- 'house' user, password testING123
INSERT INTO users (id, name, username, hash_password) VALUES (666, 'house', 'house', 'pbkdf2:sha256:150000$VgI2Za0B$d77616efc62f71f437a0f72669ebb450513849b2456ba53f4c76459358ee85dd');
