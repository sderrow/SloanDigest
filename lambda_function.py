import boto3
import json
import uuid
from datetime import datetime

s3 = boto3.resource("s3")
bucket = s3.Bucket("sloandigest")


def load_sloangroups():
    # bucket.Object("sloangroups.json").download_file('/tmp/sloangroups.json')
    # with open('/tmp/sloangroups.json', 'r') as f:
    #     print(f.read())
    # return True

    sloangroups_file = bucket.Object("sloangroups.json")
    txt = sloangroups_file.get()['Body'].read().decode('utf-8')
    txt_j = json.loads(txt)["value"]
    return txt_j


def parse_date(event_date):
    dt = datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S")
    wkdy = dt.strftime("%A")
    mth = dt.strftime("%B")
    nub = int(dt.strftime("%d"))
    if nub == 1:
        ext = 'st'
    elif nub == 2:
        ext = 'nd'
    elif nub == 3:
        ext = 'rd'
    else:
        ext = 'th'
    return "{}, {} {:d}{}".format(wkdy, mth, nub, ext)


def craft_sloangroups():
    js = load_sloangroups()
    txt = "I'll start with events on SloanGroups. . "

    first = js[0]
    txt += "First, consider taking part in a {} event, hosted by the {}. The name of the event is {}. . There are already {} people planning to participate. Join them on {}. . ".format(
        first["eventType"],
        first["group"],
        first["title"],
        first["registrations"],
        parse_date(first["eventDate"])
    )

    return txt


def load_key_academics():
    return ""


def craft_key_academics_text():
    begin = "In key academic dates, "
    content = load_key_academics()
    return begin + content


def load_meet_sloanie():
    return ""


def craft_meet_sloanie():
    begin = "For today's Meet a Sloanie, "
    content = load_meet_sloanie()
    return begin + content


def load_shoutouts():
    return ""


def craft_shoutouts():
    begin = "Lastly, here are today's Shoutouts! "
    content = load_shoutouts()
    return begin + content


def create_main_text():
    return craft_sloangroups()


def create_feed():
    uid = str(uuid.uuid4())
    current_datetime = datetime.utcnow()
    title = "SloanDigest for MBA First Years"
    main_text = create_main_text()

    item = {
        "uid": uid,
        "updateDate": "{}.0Z".format(current_datetime.strftime("%Y-%m-%dT%H:%M:%S")),
        "titleText": title,
        "mainText": main_text
    }

    return item


def export_news_data(digest):
    obj = bucket.Object("SloanDigest.JSON")
    response = obj.put(
        ACL="public-read",
        Body=json.dumps(digest, ensure_ascii=False),
        ContentEncoding="utf-8",
        ContentType="application/json"
    )
    print(response)


def lambda_handler(event, context):
    news = create_feed()
    export_news_data(news)


lambda_handler("", "")