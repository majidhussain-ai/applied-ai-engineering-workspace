
--  Retrieving data from table 
SELECT post_content 
FROM my_post

-- Also retrieviing data from single table databse 
SELECT total_balance
from my_earn_money_table

-- Retrieving all columns from table 
SELECT * FROM users;
SELECT * FROM my_post;

-- using inner join to retrieve just matching user_ids rows 
SELECT 
    users.username,
    my_post.post_content
FROM users
INNER JOIN my_post ON users.id = my_post.user_id;

-- new cretead table checking
SELECT * FROM ai_agent
-- filtering query
SELECT name, model, temperature 
FROM ai_agent
WHERE is_active = False
    AND model ILIKE '%Gemini%' 
ORDER BY temperature ASC;

-- challenge problem2 sol
SELECT agent_name, agent_model, temperature, is_active
FROM active_agent
WHERE is_active = True 
AND agent_model ILIKE '%gemini%'
ORDER BY temperature ASC;

-- UPDATE task
UPDATE active_agent 
SET temperature = temperature + 0.2 
WHERE is_active = True 
AND agent_model ILIKE '%gemini%'
RETURNING agent_name, agent_model, temperature;

-- Delete task
DELETE FROM active_agent 
WHERE is_active = False AND temperature > 0.4
RETURNING active_id , agent_name, temperature;

-- Read with pagination
SELECT agent_name, agent_name, temperature
FROM active_agent
WHERE is_active = True
ORDER BY agent_name ASC
LIMIT 3 OFFSET 3;

SELECT * FROM active_agent;

update active_agent
set agent_name = 'gemini-2.0-flash', temperature = greatest(0.1 , temperature - 0.2)
where is_active = True
and agent_model ilike '%1.5%'

DELETE FROM app_users 
where email = 'majid@gmail.com';

-- joining operations on joint table (multi-linked)
SELECT * from my_earn_money;

-- joining just between 2 tables 
SELECT 
        u.user_name,
        p.post_content,
        p.created_at
FROM users u 
inner JOIN my_post p ON u.id = p.user_id ;
        
-- joining 3 tables 
SELECT 
    u.user_name AS comment_maker,
    p.post_content AS original_post,
    c.comment_text AS comment_given
FROM my_comment c
INNER JOIN users u ON c.user_id = u.id          -- Pehla join: comment karne wale user ki details
INNER JOIN my_post p ON c.post_id = p.id;        -- Doosra join: kis post par comment kiya gaya

-- more than 3 tables joining
SELECT 
    u.user_name AS 



