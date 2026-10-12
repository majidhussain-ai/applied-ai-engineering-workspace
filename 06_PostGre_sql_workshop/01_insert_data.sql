-- simple insertion in table 
INSERT INTO users(username)
VALUES ('majid_ai_eng') 
returning id,username;

-- insertion with multi-value in table 
INSERT INTO my_post(user_id, post_content)
VALUES ('03b7cf3a-aa02-4076-82f9-8632499ecadf',
        'I am learning postgres for my applied ai engineering journey of beginner level practice'
        );

INSERT INTO my_comments(user_id, comment_text)
VALUES ('03b7cf3a-aa02-4076-82f9-8632499ecadf',
        'Hy! It is great news to now you are learning postgres for vector dbs'
        );

INSERT INTO my_earn_money_table(user_id, total_balance)
VALUES ('03b7cf3a-aa02-4076-82f9-8632499ecadf',
        '1500.0'
);

-- insertion of multi-rows at a time with upsert method 
INSERT INTO ai_agent (name, model, temperature, is_active)
VALUES 
        ('Research Summarizer','claude-3.5-sonnet',0.3 ,True),
        ('Coder for coding', 'claude-3.8-mythos', 0.7, False),
        ('Travel Agent', 'Gemini-3.4-oppos', 0.4, False),
        ('Personal RAG Agent', 'opanai-3.4o-small', 0.5, True)
ON CONFLICT (name) DO NOTHING
RETURNING agent_id , name, created_at;


-- insertion with conflict of same agent_name of any of same name 
INSERT INTO active_agent (agent_name, agent_model, temperature, is_active)
VALUES 
        ('Researcher Agent', 'gemini-3.8-flash', 0.4, True),
        ('Traveler Agent', 'gemini-3.6-flash', 0.5, False),
        ('Coder Agent', 'claude-3.4-sonnet', 0.7, True),
        ('Analytics Agent', 'openai-4o-small', 0.5, False),
        ('Summarizer Agent', 'llama-3b', 0.4, True),
        ('personal Agent', 'hugging-transformer', 0.4, False),
        ('RAG Agent', 'gemini-3.7-flash', 0.4, TRUE),
        ('Researcher Agent', 'claude-3.8-mythos', 0.4, TRUE) 
ON CONFLICT (agent_name, agent_model)
DO UPDATE SET 
        temperature = EXCLUDED.temperature,
        is_active = EXCLUDED.is_active  
RETURNING active_id, agent_name, agent_model, created_at;


update active_agent
set agent_model = 'gemini-2.0-flash', temperature = greatest(0.1 , temperature - 0.2)
where is_active = True
and agent_model ilike 'gemini-3.8-flash';

SELECT * FROM active_agent;

INSERT INTO active_agent (agent_name, agent_model, temperature, is_active)
VALUES 
        (TRIM('  Chat Agent'), LOWER('GEMINI-1.5-Pro'), ROUND(0.321, 1), True),
        (INITCAP('customer bot'), 'claude-3.5-sonnet', 0.5, True),
        (TRIM(' SQL Researcher '), 'gemini-3.6-flash', 0.7, False)
ON CONFLICT (agent_name) DO UPDATE
SET agent_name = EXCLUDED.agent_name, temperature = EXCLUDED.temperature
RETURNING active_id, agent_name , created_at;

-- linked table feeding data 
SELECT * FROM chat_session;

BEGIN;
WITH inserted_user AS(
        INSERT INTO app_users(full_name, email, is_active)
        VALUES ('Majid Hussain', 'majid@gmail.com', True),
                ('Amjad Hussain', 'amjad@gmail.com', True),
                ('Amir Hussain', 'amir@gmail.com', True)
        RETURNING user_id, email
)
        
INSERT INTO chat_session(user_id,title, total_token)
SELECT user_id, 'FastAPI connection Thread', 200 FROM inserted_user WHERE email = 'majid@gmail.com'
UNION ALL 
SELECT  user_id , 'LLM connection problem', 250 FROM inserted_user WHERE email = 'amjad@gmail.com';

COMMIT;

ROLLBACK;

-- puting data into multi linked tables
SELECT * from my_earn_money; 
BEGIN;

-- Purana data saaf kar dein taake duplicate key error na aaye (CASCADE se related tables bhi khali ho jayengi)
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- 1. Insert 6 Users with explicit column aliases
WITH inserted_user AS (
    INSERT INTO users(user_name, user_email)
    VALUES 
        ('majidhussain_ai', 'majid@gmail.com'), 
        ('amjad_hussain_ai', 'amjad@gmail.com'), 
        ('amir_khan_ai', 'amir@gmail.com'),
        ('ali_khan_ai', 'ali@gmail.com'),
        ('bilal_ahmed_ai', 'bilal@gmail.com'),
        ('zainab_ai', 'zainab@gmail.com')
    RETURNING id AS user_id, user_name AS name
),

-- 2. Insert Multiple Posts using alias 'iu' for inserted_user
inserted_post AS (
    INSERT INTO my_post(user_id, post_content)
    SELECT iu.user_id, 'Completed Python Week 1 & 2 Asyncio' FROM inserted_user iu WHERE iu.name = 'majidhussain_ai'
    UNION ALL
    SELECT iu.user_id, 'Starting PostgreSQL and pgvector for AI' FROM inserted_user iu WHERE iu.name = 'majidhussain_ai'
    UNION ALL
    SELECT iu.user_id, 'Building high-concurrency FastAPI endpoints' FROM inserted_user iu WHERE iu.name = 'amjad_hussain_ai'
    UNION ALL
    SELECT iu.user_id, 'Learning Docker Compose for microservices' FROM inserted_user iu WHERE iu.name = 'amjad_hussain_ai'
    UNION ALL
    SELECT iu.user_id, 'Understanding RAG architecture with Qdrant' FROM inserted_user iu WHERE iu.name = 'amir_khan_ai'
    UNION ALL
    SELECT iu.user_id, 'Mastering vector embeddings and similarity search' FROM inserted_user iu WHERE iu.name = 'ali_khan_ai'
    RETURNING id AS post_id, user_id AS post_user_id
),

-- 3. Insert Multiple Comments using alias 'ip' for inserted_post and explicit subquery aliases
inserted_comment AS (
    INSERT INTO my_comment(user_id, post_id, comment_text)
    (
        SELECT 
            (SELECT iu.user_id FROM inserted_user iu WHERE iu.name = 'amjad_hussain_ai') AS comment_user_id,
            ip.post_id,
            'Awesome progress Majid!' AS comment_text
        FROM inserted_post ip LIMIT 1
    )
    UNION ALL
    (
        SELECT 
            (SELECT iu.user_id FROM inserted_user iu WHERE iu.name = 'amir_khan_ai') AS comment_user_id,
            ip.post_id,
            'Keep it up brother!' AS comment_text
        FROM inserted_post ip LIMIT 1
    )
    UNION ALL 
    (
        SELECT 
            (SELECT iu.user_id FROM inserted_user iu WHERE iu.name = 'majidhussain_ai') AS comment_user_id,
            ip.post_id,
            'Very helpful post for beginners.' AS comment_text
        FROM inserted_post ip OFFSET 1 LIMIT 1
    )
    UNION ALL 
    (
        SELECT 
            (SELECT iu.user_id FROM inserted_user iu WHERE iu.name = 'zainab_ai') AS comment_user_id,
            ip.post_id,
            'Amazing work on Applied AI engineering!' AS comment_text
        FROM inserted_post ip OFFSET 2 LIMIT 1
    )
    UNION ALL 
    (
        SELECT 
            (SELECT iu.user_id FROM inserted_user iu WHERE iu.name = 'bilal_ahmed_ai') AS comment_user_id,
            ip.post_id,
            'Thanks for sharing this great roadmap.' AS comment_text
        FROM inserted_post ip OFFSET 3 LIMIT 1
    )
    UNION ALL 
    (
        SELECT 
            (SELECT iu.user_id FROM inserted_user iu WHERE iu.name = 'ali_khan_ai') AS comment_user_id,
            ip.post_id,
            'Clear and easy to understand concepts.' AS comment_text
        FROM inserted_post ip OFFSET 4 LIMIT 1
    )
    RETURNING id AS comment_id, user_id AS comment_user_id, comment_text
)

-- 4. Insert Earnings records using alias 'ic' for inserted_comment
INSERT INTO my_earn_money(user_id, comment_id, total_balance)
SELECT ic.comment_user_id, ic.comment_id, 150.00 FROM inserted_comment ic
UNION ALL
SELECT ic.comment_user_id, ic.comment_id, 220.50 FROM inserted_comment ic LIMIT 3;

COMMIT;

ROLLBACK;