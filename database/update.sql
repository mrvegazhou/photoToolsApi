-- 更改日期字段
ALTER TABLE app.app_user ADD COLUMN create_time_holder TIMESTAMP with time zone NULL;
ALTER TABLE app.app_user ALTER COLUMN delete_time TYPE TIMESTAMP with time zone USING create_time_holder;
ALTER TABLE app.app_user DROP COLUMN create_time_holder;

CREATE SEQUENCE app.app_feedback_reply_uuid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;