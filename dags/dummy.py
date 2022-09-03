from datetime import datetime

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

with DAG("my_dag", start_date=datetime(2022, 9, 3)) as dag:
    dummy_operator_1 = DummyOperator("dummy1")
    dummy_operator_2 = DummyOperator("dummy2")
    dummy_operator_3 = DummyOperator("dummy3")
    dummy_operator_4 = DummyOperator("dummy4")
    dummy_operator_5 = DummyOperator("dummy5")
    dummy_operator_6 = DummyOperator("dummy6")
    dummy_operator_7 = DummyOperator("dummy7")

    (
        dummy_operator_1
        >> dummy_operator_2
        >> dummy_operator_3
        >> [dummy_operator_4, dummy_operator_5, dummy_operator_6, dummy_operator_7]
    )
