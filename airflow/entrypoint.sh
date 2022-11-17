#!/bin/sh

wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
apt-get update && \
apt-get install -y google-chrome-stable

echo "Chrome install success, 5 seconds waiting..."
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