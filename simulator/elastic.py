import time

import boto3
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def ssm_param(ssm_client, param: str) -> str:
    response = ssm_client.get_parameter(Name=f"/spark_simulation_app/{param}", WithDecryption=True)
    return response['Parameter']['Value']


class Elastic:
    ssm_client = boto3.client("ssm", region_name="us-east-1")
    cloud_id = ssm_param(ssm_client, "cloud_id")
    username = ssm_param(ssm_client, "username")
    password = ssm_param(ssm_client, "password")

    @staticmethod
    def load_sim_data(_covid_df, _stats_df):
        """Wrapper to load simulation data"""

        # make a copy so original values are not transformed
        covid_df = _covid_df.copy()
        stats_df = _stats_df.copy()

        # transform the values in covid_df for legend
        D = {
            0: 'Healthy',
            1: 'Infected',
            666: 'Dead',
            115: 'Hospitalized',
            7: 'Cured'
        }
        for k, v in D.items():
            covid_df.loc[covid_df['Covid-19'] == k, 'Covid-19'] = v

        # transform the values in stats_df for legend and to show multicolor lines
        temp_df = pd.DataFrame(columns=['day', 'status', 'value'])
        eco_df = pd.DataFrame(columns=['day', 'percentage', 'type'])
        stats_df = stats_df.drop(['simulationID', 'Work'], axis=1)
        for i in range(len(stats_df)):
            for col in stats_df.columns:
                doc = {'day': i, 'status': col, 'value': stats_df.loc[i][col]}
                temp_df = temp_df.append(doc, ignore_index=True)
            eco_df = eco_df.append(
                {
                    'day': i,
                    'percentage': _stats_df.loc[i]['Work'],
                    'type': 'Work'
                },
                ignore_index=True)
            eco_df = eco_df.append(
                {
                    'day': i,
                    'percentage': 50,
                    'type': 'Threshold'
                },
                ignore_index=True)

        stats_df = temp_df

        Elastic.load_data(covid_df, "covid_df")
        Elastic.load_data(stats_df, "stats_df")
        Elastic.load_data(eco_df, "eco_df")

    @staticmethod
    def load_data(data, index):

        es = Elasticsearch(cloud_id=Elastic.cloud_id,
                           http_auth=(Elastic.username, Elastic.password))

        # to make the index if it doesn't exist
        es.index(index, data.iloc[0].to_json(), id=0)

        # Bulk insert
        actions = [{
            "_index": index,
            "_type": "_doc",
            "_id": j,
            "_source": data.loc[j].to_json()
        } for j in range(0, len(data))]

        st = time.time()
        helpers.bulk(es, actions)
        end = time.time()
        print("total time to bulk insert", end - st)

        es.indices.refresh(index=index)

    @staticmethod
    def delete_data(index, id_range):
        es = Elasticsearch(cloud_id=Elastic.cloud_id,
                           http_auth=(Elastic.username, Elastic.password))
        # Bulk delete
        actions = [{
            "_op_type": 'delete',
            "_index": index,
            "_id": j,
        } for j in range(0, id_range)]
        st = time.time()
        helpers.bulk(es, actions)
        end = time.time()
        print("total time to bulk delete", end - st)

    @staticmethod
    def clear_data(index):
        es = Elasticsearch(cloud_id=Elastic.cloud_id,
                           http_auth=(Elastic.username, Elastic.password))
        es.delete_by_query(index, body={"query": {"match_all": {}}})
