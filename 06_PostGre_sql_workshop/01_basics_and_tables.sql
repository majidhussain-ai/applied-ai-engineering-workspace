-- linked table through foreign key on applying operations later 

DROP TABLE IF EXISTS my_earn_money CASCADE;
DROP TABLE IF EXISTS my_comment CASCADE;
DROP TABLE IF EXISTS my_post CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- users table 1
CREATE TABLE IF NOT EXISTS users(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_name TEXT NOT NULL UNIQUE,
    user_email TEXT NOT NULL UNIQUE, 
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- post table 2
CREATE TABLE IF NOT EXISTS my_post(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    post_content TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_post_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
); 

-- comment table 3
CREATE TABLE IF NOT EXISTS my_comment(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    post_id UUID NOT NULL,
    comment_text TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES users(id) ON delete CASCADE,
    CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES my_post(id) ON delete CASCADE
);

-- earned money table4
CREATE TABLE IF NOT EXISTS my_earn_money(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    comment_id UUID,
    total_balance NUMERIC(10, 2) DEFAULT 0.00 CHECK(total_balance >= 0),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_earn_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_earn_comment FOREIGN KEY (comment_id) REFERENCES my_comment(id) ON DELETE SET NULL
);

-- Problem questions Ch1
CREATE TABLE IF NOT EXISTS ai_agent(
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE ,
    model TEXT NOT NULL,
    temperature NUMERIC(2,1) DEFAULT 0.3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS active_agent CASCADE;
-- Read challege 

CREATE TABLE IF NOT EXISTS active_agent (
        active_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        agent_name TEXT NOT NULL,
        agent_model TEXT NOT NULL,
        temperature NUMERIC DEFAULT 0.4,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_agent_name_model UNIQUE (agent_name, agent_model)
);

-- Test challenge: table 1 
CREATE TABLE IF NOT EXISTS app_users(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    is_active BOOLEAN DEFAULT True,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- table 2 linked with foregn key 
CREATE TABLE IF NOT EXISTS chat_session(
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(user_id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'new conversation',
    total_token INTEGER DEFAULT 0 CHECK(total_token>=0),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);