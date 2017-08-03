SELECT users.username  
             FROM thomas.projectusers 
             INNER JOIN thomas.users ON projectusers.username=users.username 
             INNER JOIN thomas.projects ON projectusers.project=projects.project
             WHERE  institute_id LIKE "%INSTITUTE%" 
