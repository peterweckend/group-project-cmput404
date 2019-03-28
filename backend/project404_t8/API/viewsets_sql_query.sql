-- 1: selected>Just Me
-- 2: Specific User(s)
-- 3: All Friends
-- 4: Friends of Friends
-- 5: Only Friends on Connectify
-- 6: Public
-- UNLISTED OPTION

-- posts: posts satisfying 1, 3, 4, 6
WITH posts AS
    (SELECT id FROM API_post WHERE author_id in  
        -- >>>>>>>>>> gets ids matching #4: friend of friends <<<<<<<<<<
        (SELECT f2.friend_a_id AS fofid 
            FROM API_friendship f 
            JOIN API_friendship f2 ON f.friend_a_id = f2.friend_b_id 
            WHERE fofid NOT IN 
                (SELECT friend_a_ID FROM API_friendship  
                WHERE friend_b_id = %s) 
            AND 
                f.friend_b_id = %s AND fofid != %s) 
        AND privacy_setting = 4 
        -- >>>>>>>>>> ------------------------------------- <<<<<<<<<<
    
    UNION
    
    -- >>>>>>>>>> gets posts satisfing #1, #3, #5, #6 <<<<<<<<<<
    SELECT id FROM API_post WHERE 
        (author_id in  
            (WITH friends(fid) AS 
                (SELECT friend_b_id FROM API_friendship WHERE friend_a_id=%s) 
                SELECT * FROM friends WHERE fid != %s GROUP BY fid)
            AND 
            (   privacy_setting = 3 OR -- dealing with #3
                privacy_setting = 4 OR
            (   privacy_setting = 5 AND original_host = --dealing with #5
            (select host from users_customuser where id = %s))))
        OR author_id = %s OR  privacy_setting = 6) -- dealing with #1 and #6
    -- >>>>>>>>>> -------------------------------- <<<<<<<<<<

SELECT * FROM API_post WHERE id in posts 
    AND 
    -- >>>>>>>>>> address UNLISTED posts <<<<<<<<<<
    (is_unlisted = 0 OR 
    (is_unlisted = 1 AND author_id = %s))
    -- >>>>>>>>>> ---------------------- <<<<<<<<<<