# Todo-List
## 1) Query to create users and todos tables
```
create extension citext;
```
```
create table users (
    id serial primary key,
    name citext not null,
    email citext unique,
    created_at timestamptz default now()
);
```
```
create table todos (
    id serial primary key,
    title citext not null,
    user_id integer references users (id) on delete cascade,
    is_completed boolean default false,
    created_at timestamptz default now()
);
```
## 2) Inserting sample users and todos
```
insert into
    users (name, email)
values ('User 1', 'user1@example.com'),
    ('User 2', 'user2@example.com'),
    ('User 3', 'user3@example.com');
```
![users table with sample data](https://github.com/hs-4419/Todo-List/blob/main/Images/Users%20table%20intial%20insertion.png)
```
insert into
    todos (title, user_id)
values ('Todo 1', 1),
    ('Todo 2', 1),
    ('Todo 3', 2),
    ('Todo 4', 2),
    ('Todo 5', 3);
```
![todos table with sample data](https://github.com/hs-4419/Todo-List/blob/main/Images/Todos%20table%20intial%20insertion.png)
## 3) Updating is_completed status of a todo by id
__Table before executing the query__
</br>__Query__
```
update todos set is_completed = true where id = 2;
```
__Table snapshot before and after executing the query__</br>
![Table after updating is_completed](https://github.com/hs-4419/Todo-List/blob/main/Images/is_completed%20updated%20to%20true.png)
## 4) Fetch all todos for a specific user, ordered by creation date
```
select * from todos where user_id = 1 order by created_at ASC;
select * from todos where user_id = 2 order by created_at DESC;
```
![Table snapshot for all todos for a user ordered by creation date](https://github.com/hs-4419/Todo-List/blob/main/Images/Fetching%20todos%20for%20specific%20user.png)
## 5) Adding due_date column in todos table
```
alter table todos add column due_date timestamptz;
```
```
alter table todos
alter column due_date set default now() + interval '7 day';
```
```
update todos
set "due_date" = "created_at" + interval '1 day'
where "id" in (1, 2, 3);
```
```
update todos
set "due_date" = "created_at" + interval '7 day'
where "id" in (4, 5, 6);
```
![Added due_date column](https://github.com/hs-4419/Todo-List/blob/main/Images/Added%20due_date%20column.png)
## 6) Fetching all overdue todos, ordered by due date
```
select *
from todos
where
    due_date < now()
    and is_completed = false
order by due_date asc;
```
## 7) Find no. of todos each user has, grouped by user_id
```
select user_id, count(*) as "No. of todos"
from todos
group by user_id;
```
## 8) Adding description column in todos table
```
alter table todos add column description text;
```
```
update todos
set description = 'Description for todo' || id
where id in (1, 2, 3, 4, 5, 6);
```
![Added desc column](https://github.com/hs-4419/Todo-List/blob/main/Images/Added%20description%20column.png)
## 9) Delete a user
```
delete from users where id = 3;
```
>Cascade delete is handled while `todos` table creation
## 10) Fetch latest todo of each user with their name
```
select distinct on(todos.user_id) users.name, todos.*
from todos
join users on todos.user_id = users.id
order by todos.user_id, todos.created_at desc;
```
## 11) SQL query to generate a report showing the number of completed and uncompleted todos for each user, along with the user's name and email.
```
select u.id, u.name, u.email,
       count(case when t.is_completed = true then 1 end) as total_completed,
       count(case when t.is_completed = false then 1 end) as total_uncompleted
from users u
left join todos t on u.id = t.user_id
group by u.id, u.name, u.email;
```
![count of completed and uncompleted](https://github.com/hs-4419/Todo-List/blob/main/Images/totalCompleted%20and%20totalUncompleted.png)
## 12) Modifying is_completed column to status column with 3 possible values (pending, in_progress, completed)
```
create type todos_is_completed_enum as enum ('pending', 'in_progress', 'completed');
```
```
alter table todos
alter column is_completed drop default,
alter column is_completed type todos_is_completed_enum 
using case when is_completed = true then 'completed'::todos_is_completed_enum 
else 'pending'::todos_is_completed_enum end,
alter column is_completed set default 'pending';
```
![is_completed updated to enum](https://github.com/hs-4419/Todo-List/blob/main/Images/is_completed%20updated%20to%20enum.png)
```
alter table todos rename column is_completed to status;
```
## 13) Scaling Up
__Observations while bulk inserting__
- Faced no difficulty in inserting records till 10M users and 100M todos
- Ran out of memory while inserting 1B todos after inserting 100M users
- It occured because I was first storing all the records in the memory and then sending it in batches to the database
- Fixed this by generating only the records which were to be sent to database i.e 100,000
- Later was able to insert 1B records in batches of 100,000 todos per batch, but it took 8.5+ hours
- NO SCREENSHOTS OF TIMING AS APPLICATION CRASHED
## 14) Query to fetch all todos where status is not completed and were created within last 7 days
```
select * from todos
where status != 'completed'
and created_at >= now() - interval '7 day'
order by id;
```
## 15) Time taken to fetch todos for a user
__100K+ todos__
![Time taken to fetch 100K+ todos for a user](https://github.com/hs-4419/Todo-List/blob/main/Images/Querying%20todo%20for%20a%20user%20with%20100K%2B%20todos.png)
__1M+ todos__
![Time taken to fetch 1M+ todos for a user](https://github.com/hs-4419/Todo-List/blob/main/Images/Querying%20todo%20for%20a%20user%20with%201M%2B%20todos.png)
__10M+ todos__
![Time taken to fetch 10M+ todos for a user](https://github.com/hs-4419/Todo-List/blob/main/Images/Querying%20todo%20for%20a%20user%20with%2010M%2B%20todos.png)
__100M+ todos__
![Time taken to fetch 100M+ todos for a user](https://github.com/hs-4419/Todo-List/blob/main/Images/Querying%20todo%20for%20a%20user%20with%20100M%2B%20todos.png)
__1B+ todos__
...still running</br>
tried a few times, evertime system got crashed after half an hour
![Resource Monitor](https://github.com/hs-4419/Todo-List/blob/main/Images/System%20crashed.png)


## 16) Query to find users who have not completed any of their todos within last month
__Queries to add new column completed_at__
```
alter table todos add column completed_at timestamptz;
```
```
update todos set completed_at = now()-interval '2 day' where status='completed';
```
```
CREATE OR REPLACE FUNCTION update_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    -- If status changed to 'completed', set completed_at
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        NEW.completed_at = NOW();
    -- If status changed from 'completed' to something else, clear completed_at
    ELSIF NEW.status != 'completed' AND OLD.status = 'completed' THEN
        NEW.completed_at = NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
```
CREATE TRIGGER update_completed_at_trigger
BEFORE UPDATE ON todos
FOR EACH ROW
EXECUTE FUNCTION update_completed_at();
```
__Required Query__
```
select u.id, u.name, u.email
from users u
left join todos t ON u.id = t.user_id 
    and t.completed_at >= now() - interval '1 month'
where t.user_id is null
order by u.id;
```
## 17) 
## 18) Query to track how many todos a user completes per week
__Below query shows todos completed per week for last 4 weeks only__
```
select u.name, u.email, date_trunc('week', t.completed_at) as week_start, count(t.id) as todos_completed
from users u
left join todos t on u.id = t.user_id
and t.status = 'completed'
and t.completed_at is not null
and t.completed_at >= now() - interval '4 weeks'
group BY u.id, u.name, u.email, week_start
order BY u.id, week_start desc;
```
## 19) 










