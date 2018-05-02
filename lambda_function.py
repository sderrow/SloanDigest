import boto3
import json
import uuid
from datetime import datetime, date
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file
import pytz

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


def dt_formatter(dt):
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


def parse_date(event_date):
    dt = datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S")
    return dt_formatter(dt)


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

    second = js[1]
    txt += "Next, the {} is hosting {}, a {} event taking place on {}. You don't want to miss out! . ".format(
        second["group"],
        second["title"],
        second["eventType"],
        parse_date(second["eventDate"])
    )

    third = js[2]
    txt += "Another event you might be interested in is {}, hosted by the {}. Register on SloanGroups to join {} Sloanies on {}. . ".format(
        third["title"],
        third["group"],
        third["registrations"],
        parse_date(third["eventDate"])
    )

    fourth = js[3]
    txt += "Ready for a couple more? Because you won’t want to miss out on {}, hosted by the {} on {}. {} members of the Sloan community are attending – will you? . ".format(
        fourth["title"],
        fourth["group"],
        parse_date(fourth["eventDate"]),
        fourth["registrations"]
    )

    fifth = js[4]
    txt += " Finally, check out {}, an event taking place on {} hosted by the {}. . ".format(
        fifth["title"],
        parse_date(fifth["eventDate"]),
        fifth["group"]
    )

    return txt


def setup_google_sheets():
    store = file.Storage('credentials.json')
    creds = store.get()
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service


def scrape_key_academics():
    service = setup_google_sheets()
    SPREADSHEET_ID = '1z1A4DQRTGwE4rzh5bpNXC85J8XPs3ZsWHVOgu_C-Ioo'
    RANGE_NAME = 'Sheet1!A2:B27'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            d = datetime.strptime(row[0], "%m/%d/%Y").date()
            t = datetime.now(pytz.timezone('US/Eastern')).date()
            diff = d - t
            if diff.total_seconds() >= 0:
                return d, row[1]


def craft_key_academics_text():
    nxt_date, event = scrape_key_academics()
    txt = "In key academic dates, the next big item is {} on {}. . ".format(event, dt_formatter(nxt_date))
    return txt


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
    msg = craft_sloangroups()
    msg += craft_key_academics_text()
    return msg


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
