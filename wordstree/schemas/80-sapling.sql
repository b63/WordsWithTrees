-- insert sapling tree with only a trunk
INSERT INTO tree (tree_id, tree_name, num_branches, full_width, full_height) VALUES (5, 'sapling', 0, 1024, 1024);

-- 'house' user
INSERT INTO users (id, name, username, hash_password) VALUES (666, 'house', 'house', 'pbkdf2:sha256:150000$M30YUWW7$5ea7525df93eb4cfe23d60a8b553faf7d54dc8631cf273b1407a096910a705d4');

