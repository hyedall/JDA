#!/bin/sh

airflow db init

echo "airflow db init success, 10 seconds waiting..."
sleep 10

airflow users create \
--username admin \
--password admin \
--firstname admin \
--lastname admin \
--role Admin \
--email admin@gmail.com

echo "airflow user create success, 10 seconds waiting..."
sleep 10

airflow webserver --port 8080 & airflow scheduler