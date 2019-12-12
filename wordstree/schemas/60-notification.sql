drop table if exists notification_objects;
drop table if exists notifications;

create table notification_objects (
    "id" integer primary key autoincrement,
    "entity_type" text not null,
    "message" text not null
);

insert into notification_objects (entity_type, message) values ("login", "Welcome back!");
insert into notification_objects (entity_type, message) values ("signup", "Welcome to Words With Trees!");
insert into notification_objects (entity_type, message) values ("buy", "The branch is now yours! Check it out in your inventory.");
insert into notification_objects (entity_type, message) values ("sell-waiting", "Your branch is now in the Marketplace. We'll notify you when someone buys it.");
insert into notification_objects (entity_type, message) values ("sell-confirm", "Your branch has been bought!");
insert into notification_objects (entity_type, message) values ("insufficient-tokens", "Sorry, insuffcient tokens.");

create table notifications (
    "id" integer primary key autoincrement,
    "receiver_id" integer,
    "entity_id" integer,
    "branch_text" text,
    foreign key (receiver_id) REFERENCES users("id"),
    foreign key (entity_id) REFERENCES notification_objects("id")
);