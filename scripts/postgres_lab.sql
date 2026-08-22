-- CampusOps PostgreSQL practical lab

\echo '=== DATABASE INFO ==='

SELECT current_database();
SELECT current_user;
SELECT version();


\echo '=== TABLES ==='

\dt


\echo '=== EMPLOYEES STRUCTURE ==='

\d employees


\echo '=== DEVICES STRUCTURE ==='

\d devices


\echo '=== TICKETS STRUCTURE ==='

\d tickets


\echo '=== INDEXES ==='

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;


\echo '=== FOREIGN KEYS ==='

SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';


\echo '=== TRANSACTION + ROLLBACK DEMO ==='

BEGIN;

INSERT INTO employees (
    username,
    full_name,
    email,
    department
)
VALUES (
    'rollback.demo',
    'Rollback Demo User',
    'rollback.demo@corp.lab',
    'IT'
);

SELECT
    id,
    username,
    email
FROM employees
WHERE username = 'rollback.demo';

ROLLBACK;


\echo '=== VERIFY ROLLBACK ==='

SELECT
    id,
    username,
    email
FROM employees
WHERE username = 'rollback.demo';


\echo '=== TEMPORARY DATASET FOR QUERY ANALYSIS ==='

BEGIN;

INSERT INTO employees (
    username,
    full_name,
    email,
    department
)
SELECT
    'benchmark_user_' || number,
    'Benchmark User ' || number,
    'benchmark_' || number || '@corp.lab',
    CASE
        WHEN number % 4 = 0 THEN 'IT'
        WHEN number % 4 = 1 THEN 'Finance'
        WHEN number % 4 = 2 THEN 'Marketing'
        ELSE 'Support'
    END
FROM generate_series(1, 10000) AS number;


ANALYZE employees;


\echo '=== EXPLAIN ==='

EXPLAIN
SELECT *
FROM employees
WHERE username = 'benchmark_user_9000';


\echo '=== EXPLAIN ANALYZE: USERNAME INDEX ==='

EXPLAIN ANALYZE
SELECT *
FROM employees
WHERE username = 'benchmark_user_9000';


\echo '=== EXPLAIN ANALYZE: DEPARTMENT ==='

EXPLAIN ANALYZE
SELECT *
FROM employees
WHERE department = 'IT';


\echo '=== ROW COUNT INSIDE TRANSACTION ==='

SELECT COUNT(*) AS employee_count
FROM employees;


ROLLBACK;


\echo '=== TEMPORARY DATA REMOVED ==='

SELECT COUNT(*) AS benchmark_users_remaining
FROM employees
WHERE username LIKE 'benchmark_user_%';


\echo '=== ALEMBIC VERSION ==='

SELECT *
FROM alembic_version;


\echo '=== POSTGRESQL LAB COMPLETE ==='