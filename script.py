import psycopg2
import psycopg2.extras  # Import the extras module
from config import load_config
from connect import connect
import time
import random

page_size = 100000  # Number of records to insert per batch

def generate_random_todo_description():
    """
    Generates a random sentence for todo descriptions.
    """
    subjects = [
        "Review the project requirements", "Complete the documentation", "Schedule the meeting",
        "Update the database schema", "Fix the bug in authentication", "Implement the new feature",
        "Test the user interface", "Optimize the database queries", "Deploy to production server",
        "Create the user manual", "Backup the important data", "Configure the security settings",
        "Analyze the performance metrics", "Design the new workflow", "Integrate with third-party API",
        "Refactor the legacy code", "Validate the input forms", "Setup the monitoring system",
        "Train the new team members", "Plan the next sprint goals"
    ]
    
    actions = [
        "before the deadline approaches", "to improve system performance", "for better user experience",
        "according to best practices", "with proper error handling", "using modern standards",
        "following security guidelines", "to meet client requirements", "for scalability purposes",
        "with comprehensive testing", "including edge cases", "for maintainability",
        "considering performance impact", "with proper documentation", "following team conventions",
        "to reduce technical debt", "for better code quality", "with user feedback integration",
        "ensuring data consistency", "with automated monitoring"
    ]
    
    return f"{random.choice(subjects)} {random.choice(actions)}."

def generate_random_todo_title():
    """
    Generates a random todo title.
    """
    verbs = [
        "Fix", "Update", "Create", "Review", "Test", "Deploy", "Optimize", "Configure",
        "Implement", "Design", "Analyze", "Schedule", "Complete", "Backup", "Setup",
        "Validate", "Integrate", "Refactor", "Train", "Plan", "Monitor", "Debug",
        "Install", "Migrate", "Document", "Organize", "Merge", "Build", "Patch"
    ]
    
    objects = [
        "user authentication system", "database queries", "API endpoints", "user interface",
        "payment gateway", "email notifications", "security settings", "backup system",
        "monitoring dashboard", "error handling", "data validation", "user permissions",
        "search functionality", "mobile responsiveness", "performance metrics", "log files",
        "configuration files", "third-party integrations", "code documentation", "test coverage",
        "production deployment", "staging environment", "development workflow", "bug reports",
        "feature requests", "user feedback", "system requirements", "project timeline",
        "team meetings", "code reviews", "quality assurance", "server maintenance"
    ]
    return f"{random.choice(verbs)} {random.choice(objects)}."
    
def bulk_insert_users_and_todos(users_data):
    """
    Inserts a large batch of users, and then inserts 10 todos for each new user.
    """
    sql_insert_users = "INSERT INTO users (name, email) VALUES %s RETURNING id;"
    sql_insert_todos = (
        "INSERT INTO todos (title, user_id, description) VALUES %s RETURNING id;"
    )

    config = load_config()
    start_time = time.time()
    todos_to_add = []  

    try:
        with connect(config) as conn:
            with conn.cursor() as cur:
                # === Step 1: Bulk INSERT users and get their new IDs ===
                print(f"Inserting {len(users_data)} users...")
                user_ids = psycopg2.extras.execute_values(
                    cur, sql_insert_users, users_data, fetch=True, page_size=page_size
                )
                user_insert_end_time = time.time()
                print(
                    f"Successfully inserted {len(user_ids)} users in {user_insert_end_time - start_time:.2f} seconds."
                )

                # === Step 2: Prepare todo data (10 for each new user) ===
                # user_ids is a list of tuples like [(1,), (2,)]
                for user_id_tuple in user_ids:
                    user_id = user_id_tuple[0]
                    for i in range(1, 11):  # Create 10 todos for this user
                        title = generate_random_todo_title()
                        description = generate_random_sentence()
                        todos_to_add.append((title, user_id, description))

                print(f"Prepared {len(todos_to_add)} todos for insertion.")

                # === Step 3: Bulk INSERT todos ===
                print(f"Inserting {len(todos_to_add)} todos...")
                todo_insert_start_time = time.time()
                if todos_to_add:
                    todo_ids = psycopg2.extras.execute_values(
                        cur, sql_insert_todos, todos_to_add, fetch=True, page_size=page_size
                    )
                    todo_insert_end_time = time.time()
                    print(
                        f"Successfully inserted {len(todo_ids)} todos in {todo_insert_end_time - todo_insert_start_time:.2f} seconds."
                    )

            print("Transaction committed.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        return

    end_time = time.time()
    print(
        f"\nProcessed {len(users_data)} users and {len(todos_to_add)} todos in {end_time - start_time:.2f} seconds."
    )


def bulk_insert_todos(todos_to_insert):
    """
    Inserts a large batch of todos into the database.
    """
    sql_insert_todos = (
        "INSERT INTO todos (title, user_id, description) VALUES %s RETURNING id;"
    )

    config = load_config()
    start_time = time.time()

    try:
        with connect(config) as conn:
            with conn.cursor() as cur:
                print(f"Inserting {len(todos_to_insert)} todos...")
                todo_ids = psycopg2.extras.execute_values(
                    cur, sql_insert_todos, todos_to_insert, fetch=True, page_size=page_size
                )
                todo_insert_end_time = time.time()
                print(
                    f"Successfully inserted {len(todo_ids)} todos in {todo_insert_end_time - start_time:.2f} seconds."
                )

            print("Transaction committed.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        return

    end_time = time.time()
    print(
        f"Processed {len(todos_to_insert)} todos in {end_time - start_time:.2f} seconds.\n"
    )


if __name__ == "__main__":
    """
    Commented code was used to bulk insert user and 10 todos per new user
    """
    # already_inserted_users_count = 1000 + 3 + 4000000 + 10000000
    # Generating list of tuples for users
    # print("Inserting 100M dummy users and 1B todos...")
    # users_to_add = [
    #     (f"User{i}", f"user{i}@example.com")
    #     for i in range(
    #         already_inserted_users_count + 1, already_inserted_users_count + 1 + 100000000
    #     )
    # ]
    # bulk_insert_users_and_todos(users_to_add)

    """
    Later this code was used to bulk insert 1B todos
    """
    todo_size = 1000000000
    todo_per_batch = page_size
    total_time = 0
    
    for _ in range(todo_size // todo_per_batch):
        todos_to_add = [(generate_random_todo_title(), 4, generate_random_todo_description()) for _ in range(1, todo_per_batch + 1)]
        start_time = time.time()
        bulk_insert_todos(todos_to_add)
        end_time = time.time()
        total_time += end_time - start_time
    
    print("--------------------------------------------------")
    print(f"Total time taken for bulk inserting todos: {total_time:.2f} seconds")
    print(f"Average time per batch: {total_time / (todo_size // todo_per_batch):.3f} seconds")
    print(f"Records per second: {todo_size / total_time:,.0f}")
    print("--------------------------------------------------")
