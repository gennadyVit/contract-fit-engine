{{ config(materialized='table', schema='MARTS') }}

with source as (
    select * from GOVCONTRACT.RAW.STG_USASPENDING_AWARDS
),

cleaned as (
    select
        AWARD_ID,
        INTERNAL_ID,
        RECIPIENT_NAME,
        AWARD_AMOUNT,
        CASE
            WHEN AWARD_AMOUNT >= 1000000 THEN 'Large'
            WHEN AWARD_AMOUNT >= 100000  THEN 'Medium'
            ELSE 'Small'
        END as AWARD_SIZE_CATEGORY,
        DESCRIPTION,
        AWARDING_AGENCY,
        AWARDING_SUB_AGENCY,
        AWARD_TYPE,
        START_DATE,
        END_DATE,
        DATEDIFF('day', START_DATE, END_DATE) as CONTRACT_LENGTH_DAYS,
        POP_COUNTRY_CODE,
        POP_STATE_CODE,
        LOADED_AT

    from source
    where AWARD_AMOUNT is not null
)

select * from cleaned
