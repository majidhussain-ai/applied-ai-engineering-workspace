
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

-- left joining
SELECT 
        u.user_name,
        p.post_content,
        p.created_at
FROM users u 
LEFT JOIN my_post p ON u.id = p.user_id ;
        


-- more than 3 tables joining
SELECT 
    u.user_name AS username,
    p.post_content AS original_post,
    c.comment_text AS comment_given,
    e.total_balance
FROM my_earn_money e 
inner JOIN users u ON e.user_id = u.id
inner JOIN my_comment c ON e.comment_id = c.id
inner JOIN my_post p ON c.post_id = p.id;

-- write query that fetch comment and their writer
SELECT
    u.user_name AS username,
    c.comment_text AS comment_given
FROM users u 
inner JOIN my_comment c ON u.id = c.user_id;

-- user -> earning (total_balance) -> also mention who don't earned any single rupees
SELECT 
    u.user_name AS username,
    e.total_balance AS earning
FROM users u 
LEFT JOIN my_earn_money e ON u.id = e.user_id

SELECT * FROM users;

UPDATE users
SET
    user_name = 'zohaib_ali_ai',
    user_email = 'zohaib@gmail.com'
WHERE user_name = 'zainab_ai' and user_email = 'zainab@gmail.com';

-- user->post->comment 
SELECT 
    u.user_name as username,
    p.post_content AS original_post,
    c.comment_text AS comment_given
FROM my_comment c 
inner JOIN users u ON c.user_id = u.id
inner JOIN my_post p ON c.post_id = p.id;

-- user -> post -> comment -> earn -> time 
SELECT 
    u.user_name AS username,
    p.post_content AS original_post,
    c.comment_text AS comment_given,
    e.total_balance AS earning 
FROM my_earn_money e 
inner JOIN users u ON e.user_id = u.id
inner JOIN my_comment c ON e.comment_id = c.id
inner JOIN my_post p ON c.post_id = p.id;

-- post_ower -> post_content -> comment -> comment_user 
SELECT 
    u.user_name AS post_creator,
    p.post_content AS original_post,
    c.comment_text AS comment_given,
    uc.user_name AS commenter,
    ue.user_email AS commenter_email 
FROM my_comment c 
inner JOIN my_post p ON c.post_id = p.id
inner JOIN users u ON p.user_id = u.id
inner JOIN users uc ON c.user_id = uc.id
inner JOIN users ue ON c.user_id = ue.id

-- GROUP BY query 
SELECT post_content sum(total_balance) AS total_earned_bal
FROM my_earn_money
GROUP BY post_content;

SELECT 
    p.post_content AS original_post,
    sum(e.total_balance) AS earning 
FROM my_earn_money e 
inner JOIN users u ON e.user_id = u.id
inner JOIN my_comment c ON e.comment_id = c.id
inner JOIN my_post p ON c.post_id = p.id
GROUP BY p.post_content;

-- Where querying on joining table 
EXPLAIN analyze
SELECT 
    u.user_name AS post_creator,
    p.post_content AS original_post,
    c.comment_text AS comment_given,
    uc.user_name AS commenter 
FROM my_comment c 
inner JOIN my_post p ON c.post_id = p.id
inner JOIN users u ON p.user_id = u.id
inner JOIN users uc ON c.user_id = uc.id
WHERE u.user_name = 'majidhussain_ai'; 


-- having query with joining and groupby 
SELECT 
    p.post_content AS original_post,
    sum(e.total_balance) AS earning 
FROM my_earn_money e 
inner JOIN users u ON e.user_id = u.id
inner JOIN my_comment c ON e.comment_id = c.id
inner JOIN my_post p ON c.post_id = p.id
GROUP BY p.post_content
HAVING sum(e.total_balance)>200;


-- Now applying CRUD Operations 
UPDATE users
SET user_name = 'jaleelkhan_edu' , user_email = 'jaleel@gmail.com'
WHERE user_name = 'ali_khan_ai' AND user_email = 'ali@gmail.com'; 
-- checking update users table 
SELECT * FROM users;


-- DELETE FROM multi linked table 
-- first view to post we want to del any comment from post 
SELECT * FROM my_post;

DELETE FROM my_post
WHERE post_content = 'Learning Docker Compose for microservices';