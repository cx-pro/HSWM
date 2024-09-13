from .imports import *
from .funcs import *
from flask import Blueprint

tools = Blueprint("tools", __name__)

client_secrets_file = os.path.join(
  pathlib.Path(__file__).parent.parent, 'credentials.json')
flow = Flow.from_client_secrets_file(
  client_secrets_file=client_secrets_file,
  scopes=[
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email", "openid"
  ],
  redirect_uri=
  "https://hswm.up.railway.app/tools/callback?next=/tools/meet"
  # Replace this with your URL
)


def google_login_required(function):

  def wrapper(*args, **kwargs):
    if "google_id" not in session:
      return redirect(url_for('tools.__login'))
    else:
      return function(*args, **kwargs)

  return wrapper


@tools.route("/tools/")
def __tools_index():
  return redirect("/")


@tools.route('/tools/login')
def __login():
  authorization_url, state = flow.authorization_url()
  session['state'] = state
  return redirect(authorization_url)


@tools.route("/tools/meet_confirm")
def __meet_confirm():
  return render_template(
    "meet.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    title=
    "<div class='alert alert-warning fs-6'>本功能會創建Google Meet 會議室<br>是否同意本系統以Google日曆之活動附加會議方式新增Google Meet?</div>",
    content=
    f"""<div class="text-info">註1：意即本系統將有權限存取您的Google日曆之活動，並將該權限用於新增Google Meet 會議。</div><div class="text-warning">註2：本功能暫未通過Google驗證</div><br><div class='text-danger'>一經繼續，即表示您亦同意本網站的<a href="/policy">隱私權條款</a>。</div><br><div class='btn-group w-100 mt-5 mx-auto'>
    <a href='/tools/meet' class='btn btn-primary'>同意並繼續</a>
    <a href='/' class='btn btn-secondary'>取消</a>
    </div>""")


@tools.route("/tools/meet")
@google_login_required
def __meets():
  meet_code, event_url = create_meet()
  return render_template(
    "meet.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    title="<div class='alert alert-success'>成功創建Google Meet</div>",
    content=f"""<div class='btn-group w-50 mx-auto'>
    <a href='{meet_code}' target='_blank' class='btn btn-primary'>加入會議</a>
    <a href='{event_url}' target='_blank' class='btn btn-secondary'>查看會議活動</a>
    </div>""")


@tools.route("/tools/callback", methods=["post", "get"])
def __callback():
  flow.fetch_token(authorization_response=request.url)

  if not session['state'] == request.args['state']:
    abort(500)

  credentials = flow.credentials
  request_session = requests.session()
  cached_session = cachecontrol.CacheControl(request_session)
  token_request = grequests.Request(session=cached_session)

  id_info = id_token.verify_oauth2_token(
    id_token=credentials._id_token,
    request=token_request,
    audience=os.environ["GOOGLE_CLIENT_ID"])

  session['google_id'] = id_info.get('sub')
  session['name'] = id_info.get('name')
  return redirect(
    request.args.get("next") if request.args.get("next") else "/")


def create_meet():
  # Set up the Calendar API
  service = build('calendar',
                  'v3',
                  credentials=flow.credentials,
                  static_discovery=False)

  # Generate a random meet code
  meet_code = f"{uuid.uuid4().hex}"[:12]
  meet_code = meet_code[:3] + "-" + meet_code[4:8] + "-" + meet_code[9:]

  # Set the start and end time of the event
  # start_time = get_today('%Y-%m-%dT%H:%M:%S')
  # end_time = (datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S') +
  #             datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
  start_time = datetime.datetime.now(tz=pytz.timezone('Asia/Taipei'))
  end_time = start_time + datetime.timedelta(hours=1)

  # Create the event on your primary calendar
  event = {
    'summary': 'Google Meet',
    'location': 'Online',
    'description': '使用高中職小幫手新建了一場 Google Meet 會議。',
    'start': {
      'dateTime': start_time.isoformat(),
      'timeZone': 'Asia/Taipei',
    },
    'end': {
      'dateTime': end_time.isoformat(),
      'timeZone': 'Asia/Taipei',
    },
    'reminders': {
      'useDefault': False,
    },
    'conferenceData': {
      'createRequest': {
        'conferenceSolutionKey': {
          'type': 'hangoutsMeet'
        },
        'requestId': meet_code
      }
    },
  }

  event = service.events().insert(calendarId='primary',
                                  body=event,
                                  conferenceDataVersion=1).execute()
  return event.get("hangoutLink", "null"), event.get('htmlLink', "null")
  # print('Event created: %s' % (event.get('htmlLink')))

  # Get the event ID
  #event_id = event['id']

  # # Delete the event
  # try:
  #     service.events().delete(calendarId='primary', eventId=event_id).execute()
  #     print('Event deleted')
  # except HttpError as error:
  #     print('An error occurred: %s' % error)


@tools.route("/tools/random")
def __random_tool():
  return render_template("random.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))
