import httplib
import re
import urllib
import time


def get_mall_id():
    return 'thing3600'


def get_host():
    return get_mall_id() + '.cafe24.com'


def get_cafe24_login_host():
    return 'eclogin.cafe24.com'


def cafe24_login(mall_pw):
    conn = httplib.HTTPConnection(get_cafe24_login_host())
    conn.request('POST',
                 '/Shop/index.php',
                 'url=Run&IS_DEVSERVER=&userid_hidden=1&login_mode=1&'
                    + urllib.urlencode({'userid': get_mall_id(), 'mall_id': get_mall_id(), 'userpasswd': mall_pw})
                    + '&onnode=&submenu=&menu=&mode=&c_name=&loan_type=&addsvc_suburl=&is_multi=F',
                 {'Content-Type': 'application/x-www-form-urlencoded'})
    resp = conn.getresponse()
    assert resp.status == 200
    cookie = resp.getheader('set-cookie')
    data = resp.read()
    assert 'GMCC=' in cookie
    conn.close()
    return dict(re.findall(r"\<input type='hidden' name='(.*?)' value='(.*?)'", data))


def access_user_id_check_page(data):
    conn = httplib.HTTPConnection(get_host())
    body = urllib.urlencode(data)
    conn.request(
        'POST',
        '/admin/php/user_id_check.php',
        body,
        {'Content-Type': 'application/x-www-form-urlencoded'}
    )
    resp = conn.getresponse()
    assert resp.status == 302
    location = resp.getheader('location')
    cookie = resp.getheader('set-cookie')
    conn.close()
    return dict(location=location, cookie=cookie)


def access_manage_page(location):
    conn = httplib.HTTPConnection(get_host())
    conn.request('GET', location)
    resp = conn.getresponse()
    assert resp.status == 200
    data = resp.read()
    assert 'aMenuListSupplyPHP' in data
    conn.close()


def get_normal_user_ids(cookie):
    conn = httplib.HTTPSConnection(get_host())
    body = "mode=search&m_mode=&is_cti=&ord=regist_date&sort=&rows=all&grp_sel=1&group_no=1&is_member_auth=0&input_channel=&search_type=member_id&type=&age1=&age2=&gender=1&sales_amount=1&sales_type=&min_sales_amount=&max_sales_amount=&ord_date_kind=order_date&ord_start_date=&ord_end_date=&login_start_date=&login_end_date=&day_type=&regist_year1=2014&regist_month1=06&regist_day1=29&regist_year2=2014&regist_month2=06&regist_day2=29&mem_month1=06&mem_day1=29&mem_month2=06&mem_day2=29&visit_ip=&sOrderPrdtName=&iOrderPrdtNo=&offset=&page=&rows=all&mid_list%5B%5D=woonjoong&group_list%5B%5D=%EC%9D%BC%EB%B0%98%ED%9A%8C%EC%9B%90&member_name%5B%5D=%EC%9A%B4%EC%A4%80%EB%8F%99&mid_list%5B%5D=sasong&group_list%5B%5D=%EC%9D%BC%EB%B0%98%ED%9A%8C%EC%9B%90&member_name%5B%5D=%EC%82%AC%EC%86%A1%EB%8F%99&group_no_b=1&mg_mode=&mg_group_no_fix_flag=&mg_group_no=1"
    conn.request(
        'POST',
        '/admin/php/shop1/c/member_admin_l.php',
        body,
        {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookie}
    )
    resp = conn.getresponse()
    assert resp.status == 200
    data = resp.read()
    assert '<form name="mform" ' in data
    user_ids = re.findall(r'name="mid_list\[]" value="(.*?)"', data)
    conn.close()
    return user_ids


def is_family(data):
    return 'value-none' == re.findall(r'name="add1" value="(.*?)"', data)[0]


def get_position(data):
    return re.findall(r'name="add2" value="(.*?)"', data)[0]


def is_valid_position(position):
    is_valid_position = False
    if position == 'staff':
        is_valid_position = True
    elif position == 'leader':
        is_valid_position = True
    elif position == 'wsa':
        is_valid_position = True
    return is_valid_position


def get_position_number(position):
    position_number = 0
    if position == 'staff':
        position_number = 3
    elif position == 'leader':
        position_number = 2
    elif position == 'wsa':
        position_number = 4
    return position_number


def get_formdata(data):
    formdata = {
        'mode': re.findall(r'name=mode value="(.*?)"', data)[0],
        'use_password_hint': re.findall(r'name="use_password_hint" value="(.*?)"', data)[0],
        'member_id': re.findall(r'name=member_id value="(.*?)"', data)[0],
        'isKrFlag': re.findall(r'name="isKrFlag" value="(.*?)"', data)[0],
        'email_confirm': re.findall(r'id=email_confirm value="(.*?)"', data)[0],
        'login_id_type': re.findall(r'id=login_id_type value="(.*?)"', data)[0],
        'group_no_b': get_position_number(re.findall(r'name="add2" value="(.*?)"', data)[0]),
        'before_group_name': re.findall(r'name="before_group_name" value="(.*?)"', data)[0],
        'hint': 'hint_01',
        'hint_answer': '',
        'passwd': '',
        'passwd_re': '',
        'zip1': re.findall(r'id="zip1" size="3" maxlength="3" value="(.*?)"', data)[0],
        'zip2': re.findall(r'id="zip2" size="3" maxlength="3" value="(.*?)"', data)[0],
        'addr1': re.findall(r'id="addr1" size="35" value="(.*?)"', data)[0],
        'addr2': re.findall(r'id="addr2" size="25" value="(.*?)"', data)[0],
        'phone': re.findall(r'id="phone" class="input01" value="(.*?)"', data)[0],
        'mobile': re.findall(r'id="mobile" class="input01" value="(.*?)"', data)[0],
        'email2': re.findall(r'name="email2" value="(.*?)"', data)[0],
        'email_full_value': re.findall(r'id="email_full_value" value="(.*?)"', data)[0],
        'is_sms_old': re.findall(r'name="is_sms_old" value="(.*?)"', data)[0],
        'is_sms': re.findall(r'name="is_sms_old" value="(.*?)"', data)[0],
        'is_news_mail_old': re.findall(r'id="is_news_mail_old" value="(.*?)"', data)[0],
        'is_news_mail': re.findall(r'id="is_news_mail_old" value="(.*?)"', data)[0],
        'member_auth': re.findall(r'name="member_auth" value="(.*?)"', data)[0],
        'use_blacklist': 'F',
        'member_memo': '',
        'lunar_calendar1': re.findall(r'id="lunar_calendar1" value="(.*?)"', data)[0],
        'lunar_calendar2': re.findall(r'id="lunar_calendar2" value="(.*?)"', data)[0],
        'lunar_calendar3': re.findall(r'id="lunar_calendar3" value="(.*?)"', data)[0],
        'is_solar_calendar': 'T',
        'wedding_anniversary1': re.findall(r'id="wedding_anniversary1" value="(.*?)"', data)[0],
        'wedding_anniversary2': re.findall(r'id="wedding_anniversary2" value="(.*?)"', data)[0],
        'wedding_anniversary3': re.findall(r'id="wedding_anniversary3" value="(.*?)"', data)[0],
        'life_partner_birthday1': re.findall(r'id="life_partner_birthday1" value="(.*?)"', data)[0],
        'life_partner_birthday2': re.findall(r'id="life_partner_birthday2" value="(.*?)"', data)[0],
        'life_partner_birthday3': re.findall(r'id="life_partner_birthday3" value="(.*?)"', data)[0],
        'job': "job_00",
        'job_class': "job_class_04",
        'school': "school_00",
        'region': "region_00",
        'internet': "internet_00",
        'child': "child_00",
        'car': "car_00",
        'earning': "earning_00",
        'add1': '',
        'add2': '',
        'add3': re.findall(r'name="add3" value="(.*?)"', data)[0],
        'add4': re.findall(r'name="add4" value="(.*?)"', data)[0],
        'bank_account_owner': re.findall(r'name="bank_account_owner" value="(.*?)"', data)[0],
        'refund_bank_code': '',
        'bank_account_no': re.findall(r'name="bank_account_no" type="text" value="(.*?)"', data)[0]
    }
    return formdata


def level_up_if_family_member(cookie):
    user_ids = get_normal_user_ids(cookie)
    conn = httplib.HTTPSConnection(get_host())
    for user_id in user_ids:
        conn.request('GET', '/admin/php/shop1/c/member_admin_d_f.php?user_id=' + user_id, headers={'Cookie': cookie})
        resp = conn.getresponse()
        assert resp.status == 200
        data = resp.read()
        print 'Check up', user_id
        user_position = get_position(data)
        if is_family(data) and is_valid_position(user_position):
            form_data = get_formdata(data)
            body = urllib.urlencode(form_data)
            headers = {'Cookie': cookie,
                       'Referer': "https://" + get_host() + "/admin/php/shop1/c/member_admin_d_f.php?member_id=" + user_id,
                       'Content-Type': 'application/x-www-form-urlencoded'
            }
            conn.request('POST', '/admin/php/shop1/c/member_admin_de_02.php', body, headers=headers)
            resp = conn.getresponse()
            assert resp.status == 200
            data = resp.read()
            assert "location.href='/admin/php/shop1/c/member_admin_d_f.php?member_id=" + user_id + "'" in data
            print 'Level up', user_id, 'to', user_position
    conn.close()


print 'Cafe24 Auto Manage Group Solution.'
mall_pw = raw_input("Password : ")
print 'Ready to run.'
data = cafe24_login(mall_pw)
print 'Success to login of cafe24.'
time.sleep(1)
data = access_user_id_check_page(data)
print 'Success to get the access-page.'
time.sleep(1)
access_manage_page('/admin/php/' + data['location'])
print 'Success to certification of the access-page.'
print 'Complete to prepare.'
time.sleep(1)
while True:
    now = time.localtime()
    now_time = "Run at %04d-%02d-%02d %02d:%02d:%02d" \
               % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    print now_time
    print 'Try to management.'
    try:
        level_up_if_family_member(data['cookie'])
    except AssertionError, e:
        print e
        pass
    print 'Idling process. Please wait a moment...'
    time.sleep(100)
