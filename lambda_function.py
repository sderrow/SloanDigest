import boto3
import json
import uuid
from datetime import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file
import pytz

s3 = boto3.resource("s3")
bucket = s3.Bucket("sloandigest")


def load_sloangroups():
    sloangroups_file = bucket.Object("sloangroups.json")
    txt = sloangroups_file.get()['Body'].read().decode('utf-8')
    txt_j = json.loads(txt)["value"]
    return txt_j


def date_has_passed(d):
    t = datetime.now(pytz.timezone('US/Eastern')).date()
    diff = d - t
    return diff.total_seconds() < 0


def dt_formatter(dt):
    wkdy = dt.strftime("%A")
    mth = dt.strftime("%B")
    nub = int(dt.strftime("%d"))
    if nub in [1, 21, 31]:
        ext = 'st'
    elif nub in [2, 22]:
        ext = 'nd'
    elif nub in [3, 23]:
        ext = 'rd'
    else:
        ext = 'th'
    return "{}, {} {:d}{}".format(wkdy, mth, nub, ext)


def parse_date(event_date):
    dt = datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S")
    return dt_formatter(dt)


def parse_group(event_group):
    if event_group.lower()[-4:] == 'club':
        return "the {}".format(event_group)
    return event_group


def craft_sloangroups():
    js = load_sloangroups()

    i = 0
    for k, j in enumerate(js):
        i = k
        dt = datetime.strptime(j["eventDate"], "%Y-%m-%dT%H:%M:%S").date()
        if not date_has_passed(dt):
            break

    txt = "I'll start with events on SloanGroups. <break time=\"1s\"/> "

    first = js[i]
    txt += "First, consider taking part in a {} event, hosted by {}. The name of the event is {}. There are already {} people planning to participate. Join them on {}. <break time=\"1s\"/> ".format(
        first["eventType"],
        parse_group(first["group"]),
        first["title"],
        first["registrations"],
        parse_date(first["eventDate"])
    )

    second = js[i+1]
    txt += "Next, {} is hosting {}, a {} event taking place on {}. You don't want to miss out! <break time=\"1s\"/> ".format(
        parse_group(second["group"]),
        second["title"],
        second["eventType"],
        parse_date(second["eventDate"])
    )

    third = js[i+2]
    txt += "Another event you might be interested in is {}, hosted by {}. Register on SloanGroups to join {} Sloanies on {}. <break time=\"1s\"/> ".format(
        third["title"],
        parse_group(third["group"]),
        third["registrations"],
        parse_date(third["eventDate"])
    )

    fourth = js[i+3]
    txt += "Ready for a couple more? Because you won’t want to miss out on {}, hosted by {} on {}. {} members of the Sloan community are attending – will you? <break time=\"1s\"/> ".format(
        fourth["title"],
        parse_group(fourth["group"]),
        parse_date(fourth["eventDate"]),
        fourth["registrations"]
    )

    fifth = js[i+4]
    txt += " Finally, check out {}, an event taking place on {} hosted by {}. <break time=\"2s\"/> ".format(
        fifth["title"],
        parse_date(fifth["eventDate"]),
        parse_group(fifth["group"])
    )

    return txt


def setup_google_sheets():
    store = file.Storage('credentials.json')
    creds = store.get()
    return build('sheets', 'v4', http=creds.authorize(Http()))


def scrape_key_academics():
    global service
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
            if not date_has_passed(d):
                return d, row[1]


def craft_key_academics_text():
    nxt_date, event = scrape_key_academics()
    txt = "In key academic dates, the next big item is {} on {}. <break time=\"2s\"/> ".format(event, dt_formatter(nxt_date))
    return txt


def load_meet_sloanie():
    global service
    SPREADSHEET_ID = '1G6oJTyR7NVjN79JgW2Qf7cs2U7-EGkBL-e3LNW--hZE'
    RANGE_NAME = 'Form Responses 1!B2:N100'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            if row[-1] == "No" and row[-2] == "Yes":
                return row[:-2]


def craft_meet_sloanie():
    first, last, prog, yr, prev_job, prev_emp, town, fav1, fav2, pty1, pty2 = load_meet_sloanie()
    txt = "There are so many people to meet and learn from at Sloan! Today’s featured Sloanie is "
    txt += "{} {}! {} is a member of the {} class of {}. ".format(first, last, first, prog, yr)
    txt += "On paper, {} is a former {} from {} and is a {} native. But if you dig beneath the surface, you’ll learn {} is also a fan of {} and {}. <break time=\"1s\"/> ".format(first, prev_job, prev_emp, town, first, fav1, fav2)
    txt += "If there’s one thing to know about Sloanies, it’s that they are passionate people. For example, {} prioritizes {} and {} while at Sloan. ".format(first, pty1, pty2)
    txt += "Great to have you with us on campus {}! <break time=\"2s\"/> ".format(first)
    return txt


def create_main_text():
    msg = craft_sloangroups()
    msg += craft_key_academics_text()
    msg += craft_meet_sloanie()
    msg += "That's it for SloanDigest. Talk to you next time!"
    msg = msg.replace("&", "and")
    return msg


def create_feed():
    uid = str(uuid.uuid4())
    current_datetime = datetime.utcnow()
    title = "SloanDigest First Cut"
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


# lambda_handler("", "")
