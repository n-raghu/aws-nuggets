import csv
import json
import time
import boto3
import codecs
import itertools
from zipfile import ZipFile

from smart_open import smart_open

rsc_dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    zfile = 'datum.zip'
    tableName = 'csvdumps'
    key = 'datum/data8216.csv'
    bucket = 'boto-ops-s3-369'
    csize = 25
    s3_uri = f's3://{bucket}/{zfile}'

    t = time.time()
    stream = yield_csv_data(s3_uri, key)
    for _ in range(25):
        chunk = itertools.islice(stream, csize)
        write_to_dynamo(tableName, chunk)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "bucket": bucket,
            "source": s3_uri,
            "target": tableName,
            "records": csize,
            "time_taken": round(time.time() - t, 3)
        })
    }


def write_to_dynamo(table_name, rows, rsc_dynamodb=rsc_dynamodb):
    table = rsc_dynamodb.Table(table_name)

    with table.batch_writer(overwrite_by_pkeys=['Year', 'count']) as batch:
        for row in rows:
            batch.put_item(Item=row)


def yield_csv_data(s3_uri, key):
    with smart_open(s3_uri, 'rb') as zip_obj:
        zippo = ZipFile(zip_obj)
        with zippo.open(key, 'r') as csv_file:
            for row in csv.DictReader(codecs.getreader('utf-8')(csv_file)):
                yield row
