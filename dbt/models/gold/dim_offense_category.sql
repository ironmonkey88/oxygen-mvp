{{ config(materialized='table', schema='gold') }}

-- Gold: dim_offense_category -- one row per NIBRS top-level category.
-- 4 rows total. severity_rank is an arbitrary ordinal -- Person before
-- Property before Society before Other -- used for consistent sort
-- order in dashboards. The ordinal is editorial, not source-derived;
-- review during MVP 3 design.
select * from (values
    ('Crimes against Person',   1),
    ('Crimes against Property', 2),
    ('Crimes against Society',  3),
    ('Other',                   4)
) as t(offense_category, severity_rank)
