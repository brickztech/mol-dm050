public.members (
    id serial4 NOT NULL,
    user_id int4 DEFAULT 0 NOT NULL,
    project_id int4 DEFAULT 0 NOT NULL,
    created_on timestamp NULL,
    mail_notification bool DEFAULT false NOT NULL,
    CONSTRAINT members_pkey PRIMARY KEY (id)
);