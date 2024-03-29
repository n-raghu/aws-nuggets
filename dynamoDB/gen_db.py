import sys
import math
from uuid import uuid1 as UU1
from random import choice, shuffle
from datetime import datetime as dtm

from bson.objectid import ObjectId

from essentials import dynamo_client, departments

sal_range = list(range(100, 100000, 100))
shuffle(sal_range)


# Create Table
def create_tab(tbl, client_):
    return client_.create_table(
        TableName=tbl,
        AttributeDefinitions=[
            {
                "AttributeName": "dep",
                "AttributeType": "S"
            },
            {
                "AttributeName": "salary",
                "AttributeType": "N"
            }
        ],
        KeySchema=[
            {
                "AttributeName": "dep",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "salary",
                "KeyType": "RANGE"
            },
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1
        }
    )


# Function to Generate Record
def gen_usr(dep, tbl, sal_r=sal_range):
    uid = str(ObjectId())
    document_id = UU1().hex
    try:
        usal = sal_r.pop()
    except Exception as err:
        sys.exit(err)
    return {
        'created_stamp': {'S': dtm.utcnow().isoformat()},
        'uid': {'S': uid},
        'dep': {'S': dep},
        'document_id': {'S': document_id},
        'active': {'BOOL': True},
        'salary': {'N': str(usal)}
    }


# Create user on dynamoDB
def create_users(db_items, client):
    push_items: dict = {}
    for col_, items_ in db_items.items():
        collection_items: list = []
        for item in items_:
            collection_items.append(
                {
                    'PutRequest': {'Item': item}
                }
            )
        push_items[col_] = collection_items

    return client.batch_write_item(
        RequestItems=push_items,
        ReturnConsumedCapacity='TOTAL',
        ReturnItemCollectionMetrics='SIZE'
    )


# Create 116 test sets
def create_116_set(tname, client_, deps=departments):
    usr_items = []
    csize = 20
    for _ii in range(116):
        usr_items.append(gen_usr(choice(deps), tname))
    chunks = math.ceil(len(usr_items)/csize)
    for n in range(chunks):
        create_users({tname: usr_items[n*csize:(n+1)*csize]}, client_)


def tester(client_ = dynamo_client):
    tb_ = 'usrsalary'
    try:
        create_tab(tb_, client_)
    except Exception:
        print('Table seems exists!!!')

    create_116_set(tb_, client_,)


if __name__ == '__main__':
    tester()
