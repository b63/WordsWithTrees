-- insert sapling tree with only a trunk
INSERT INTO tree (tree_id, tree_name, full_width, full_height) VALUES (5, 'sapling', 1024, 1024);

-- 'house' user, password testING123
INSERT INTO users (id, name, username, hash_password) VALUES (666, 'house', 'house', 'pbkdf2:sha256:150000$VgI2Za0B$d77616efc62f71f437a0f72669ebb450513849b2456ba53f4c76459358ee85dd');

-- insert root branch and corresponding ownernship info
-- INSERT INTO branches (ind, depth, length, width, angle, pos_x, pos_y, tree_id) VALUES (0, 0, 0.4, 0.008, 4.71238898038469, 0.5, 0.99, 5);
-- INSERT INTO branches_ownership (branch_id, owner_id, text, price, available_for_purchase) VALUES ((SELECT last_insert_rowid()), 666, 'HOUSE OWNED', 10, 1);

