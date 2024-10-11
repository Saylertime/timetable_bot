from config_data import config
import psycopg2
import pytz

dbname = config.DB_NAME
user = config.DB_USER
password = config.DB_PASSWORD
host = config.DB_HOST

desired_timezone = pytz.timezone('Europe/Moscow')

def connect_to_db():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cursor = conn.cursor()
    conn.autocommit = True
    return conn, cursor

def close_db_connection(conn, cursor):
    cursor.close()
    conn.close()

def create_appointments_table():
    conn, cursor = connect_to_db()

    sql = """CREATE TABLE IF NOT EXISTS public.appointments 
    (
        id SERIAL PRIMARY KEY,
        date DATE,
        time TIME,
        is_available BOOL DEFAULT TRUE,
        user_id VARCHAR REFERENCES public.users(user_id) ON DELETE SET NULL,
        UNIQUE (date, time)
    );
    """
    cursor.execute(sql)
    close_db_connection(conn, cursor)

def create_users():
    conn, cursor = connect_to_db()

    sql = """CREATE TABLE IF NOT EXISTS public.users 
    (
        user_id VARCHAR NOT NULL UNIQUE,
        username VARCHAR,
        name VARCHAR,
        phone VARCHAR,
        is_busy BOOL DEFAULT FALSE,
        notifications BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(sql)
    close_db_connection(conn, cursor)


def delete_table():
    conn, cursor = connect_to_db()

    sql = """
        DROP TABLE IF EXISTS public.appointments CASCADE;
    """
    cursor.execute(sql)

    sql = """
        DROP TABLE IF EXISTS public.users CASCADE;
    """
    cursor.execute(sql)

    close_db_connection(conn, cursor)

def add_user(user_id, username='NULL'):
    conn, cursor = connect_to_db()
    create_users()
    cursor.execute('''SELECT * FROM public.users WHERE user_id = %s''', (user_id,))
    existing_user = cursor.fetchone()
    if existing_user:
        return
    else:
        sql = """INSERT INTO public.users 
                (user_id, username)
                VALUES (%s, %s);
        """
        cursor.execute(sql, (user_id, username))
    close_db_connection(conn, cursor)


def has_name(user_id):
    conn, cursor = connect_to_db()
    try:
        cursor.execute('''SELECT name FROM public.users WHERE user_id = %s''', (user_id,))
        result = cursor.fetchone()
    finally:
        close_db_connection(conn, cursor)

    return result[0] if result else None


def add_users_name(user_id, name):
    conn, cursor = connect_to_db()
    cursor.execute('''UPDATE public.users 
                        SET name = %s
                        WHERE user_id = %s''', (name, user_id,))
    close_db_connection(conn, cursor)



def all_users_from_db():
    conn, cursor = connect_to_db()
    cursor.execute('''SELECT username, name, user_id FROM public.users''')
    all_users = cursor.fetchall()
    close_db_connection(conn, cursor)
    return all_users

def add_slots_in_db(day, time):
    conn, cursor = connect_to_db()

    sql = """
        INSERT INTO public.appointments
        (date,time)
        VALUES (%s, %s)
    """
    try:
        cursor.execute(sql, (day, time))
        return True
    except psycopg2.errors.UniqueViolation:
        return False
    finally:
        close_db_connection(conn, cursor)


def all_dates_for_buttons(value):
    conn, cursor = connect_to_db()
    sql = """
    SELECT DISTINCT date
    FROM public.appointments
    WHERE is_available = %s AND date > CURRENT_DATE
    ORDER BY date;
    """
    cursor.execute(sql, (value, ))
    all_dates = cursor.fetchall()

    return all_dates


def is_busy(user_id):
    conn, cursor = connect_to_db()
    cursor.execute('''SELECT is_busy FROM public.users WHERE user_id = %s''', (user_id,))
    return cursor.fetchone()[0]

def show_free_slots(date, value):
    conn, cursor = connect_to_db()

    sql = """
    SELECT date, time
    FROM public.appointments
    WHERE is_available = %s AND date = %s
    ORDER BY time;
    """

    cursor.execute(sql, (value, date))
    all_slots = cursor.fetchall()
    free_slots = [(date, time.strftime("%H:%M")) for date, time in all_slots]
    close_db_connection(conn, cursor)

    return free_slots

def make_appointment(user_id, date, time):
    conn, cursor = connect_to_db()

    sql = """
    UPDATE public.appointments
    SET is_available = False, user_id = %s
    WHERE date = %s AND time = %s;
    """
    cursor.execute(sql, (user_id, date, time))

    sql = """
        UPDATE public.users
        SET is_busy = True
        WHERE user_id = %s;
    """

    cursor.execute(sql, (user_id, ))

    close_db_connection(conn, cursor)

def my_appointment(user_id):
    conn, cursor = connect_to_db()

    sql = """
    SELECT date, time
    FROM public.appointments
    WHERE is_available = False AND user_id = %s;
    """

    cursor.execute(sql, (user_id,))
    my_slot = cursor.fetchone()
    close_db_connection(conn, cursor)

    return my_slot

def cancel_appointment_from_bd(user_id):
    conn, cursor = connect_to_db()

    sql = """
    UPDATE public.appointments
    SET is_available = True, user_id = NULL 
    WHERE user_id = %s;
    """

    cursor.execute(sql, (user_id,))

    sql = """
        UPDATE public.users
        SET is_busy = False
        WHERE user_id = %s;
    """
    cursor.execute(sql, (user_id,))
    close_db_connection(conn, cursor)


def get_last_busy_appointment(user_id):
    conn, cursor = connect_to_db()

    sql = """
    SELECT a.date, a.time
    FROM public.appointments a
    JOIN public.users u ON a.user_id = u.user_id
    WHERE a.user_id = %s AND u.is_busy = TRUE
    ORDER BY a.id DESC
    LIMIT 1;
    """

    cursor.execute(sql, (user_id,))
    last_appointment = cursor.fetchone()

    close_db_connection(conn, cursor)

    return last_appointment

def delete_appointments_day(date):
    conn, cursor = connect_to_db()

    sql = """
    DELETE FROM public.appointments
    WHERE date = %s;
    """

    cursor.execute(sql, (date,))
    close_db_connection(conn, cursor)

def delete_appointments_slot(date, time):
    conn, cursor = connect_to_db()

    sql = """
    DELETE FROM public.appointments
    WHERE date = %s AND time = %s;
    """

    cursor.execute(sql, (date, time))
    close_db_connection(conn, cursor)

def is_notification_on(user_id):
    conn, cursor = connect_to_db()

    sql = """
    SELECT notifications
    FROM public.users
    WHERE user_id = %s;
    """

    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()[0]
    close_db_connection(conn, cursor)

    return result

def change_notifications(user_id, value):
    conn, cursor = connect_to_db()

    sql = """
    UPDATE public.users
    SET notifications = %s
    WHERE user_id = %s;
    """

    cursor.execute(sql, (value, user_id))
    close_db_connection(conn, cursor)

def all_users_with_notifications():
    conn, cursor = connect_to_db()

    sql = """
    SELECT user_id
    FROM public.users
    WHERE notifications = True;
    """

    cursor.execute(sql)
    result = cursor.fetchall()
    close_db_connection(conn, cursor)

    return [row[0] for row in result]


def all_occupied_slots_in_db():
    conn, cursor = connect_to_db()

    sql = """
        SELECT DISTINCT date, time
        FROM public.appointments
        WHERE is_available = False AND user_id IS NOT NULL AND date >= CURRENT_DATE;
    """

    cursor.execute(sql)
    result = cursor.fetchall()
    close_db_connection(conn, cursor)

    return result

def slot_occupied_by(date, time):
    conn, cursor = connect_to_db()

    sql = """
        SELECT u.name, u.username
        FROM public.appointments a
        JOIN public.users u ON a.user_id = u.user_id
        WHERE a.date = %s AND a.time = %s;
    """

    cursor.execute(sql, (date, time))
    result = cursor.fetchone()
    close_db_connection(conn, cursor)

    return result