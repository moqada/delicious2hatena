# -*- coding: utf-8 -*-
import argparse
import datetime
import os
import smtplib
import time
import urllib
import urllib2
from xml.etree import ElementTree
from email.mime.text import MIMEText
try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import SafeConfigParser

DELICIOUS_FEED_URL = 'https://api.del.icio.us/v1/posts/all'
GMAIL_HOST = 'smtp.gmail.com'
GMAIL_PORT = 587


def fetch_posts(username, password, offset):
    """ deliciousからフィードを取得して投稿リストを返す

        username    deliciousのユーザ名
        password    deliciousのパスワード
        offset      単位は分
    """
    prev_time = datetime.datetime.fromtimestamp(
        time.mktime(datetime.datetime.utcnow().timetuple()) - offset * 60)
    data = urllib.urlencode(
        {'fromdt': prev_time.strftime('%Y-%m-%dT%H:%M:0Z')})

    # Basic認証で最近のフィードを取得
    manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, DELICIOUS_FEED_URL, username, password)
    handler = urllib2.HTTPBasicAuthHandler(manager)
    opener = urllib2.build_opener(handler)
    response = opener.open(DELICIOUS_FEED_URL, data=data)
    print(u'Fetch %s?%s' % (DELICIOUS_FEED_URL, data))

    # 投稿を抽出して辞書リストにする
    elem = ElementTree.parse(response)
    posts = []
    for post in elem.findall('.//post'):
        posts.append({
            'title': post.get('description'),
            'url': post.get('href'),
            'tags': post.get('tag').split(),
            'note': post.get('extended'),
        })
        print(u'Append `%(title)s %(tags)s%(note)s`' % posts[-1])
    posts.reverse()
    return posts


def sendmail(from_addr, to_addr, posts, gmail_auth=None):
    """ deliciousの投稿を指定アドレスに送信する

        from_addr   送信元アドレス(適当なアドレス)
        to_addr     送信先アドレス(はてブで取得した投稿用アドレス)
        posts       fetch_postsで生成した投稿リスト(辞書のリスト)
        gmail_auth  SMTPにGmailを利用する場合にユーザ名、パスワードのタプル指定
    """
    charset = 'iso-2022-jp'
    if gmail_auth:
        s = smtplib.SMTP(GMAIL_HOST, GMAIL_PORT)
        s.ehlo()
        s.starttls()
        s.login(*gmail_auth)
        print(u'SMTP connected: %s' % GMAIL_HOST)
    else:
        s = smtplib.SMTP()
        s.connect()
        print(u'SMTP connected: localhost')
    for post in posts:
        body = post['url'] + '\n'
        if post['tags']:
            body += u''.join([u'[%s]' % t for t in post['tags']])
        if post['note']:
            body += post['note']
        msg = MIMEText(
            body.encode(charset, 'ignore'), 'plain', charset)
        msg['Subject'] = post['title'].encode(charset, 'ignore')
        msg['From'] = from_addr
        msg['To'] = to_addr
        s.sendmail(from_addr, [to_addr], msg.as_string())
        print(u'Sent `%s` to %s.' % (post['title'], to_addr))
    s.close()
    print(u'SMTP closed')


def command():
    parser = argparse.ArgumentParser(
        description=u'deliciousのブックマークをはてブに送信します')
    parser.add_argument(
        'offset', type=int,
        help=u'現在時刻からのオフセット(分)、この時間より新しい投稿が対象になる')
    parser.add_argument(
        '--config', default='~/.d2h',
        help=u'設定ファイルのパス、デフォルト:~/.d2h')
    parser.add_argument(
        '--delicious-username', dest='delicious_username',
        help=u'deliciousのユーザ名')
    parser.add_argument(
        '--delicious-password', dest='delicious_password',
        help=u'deliciousのパスワード')
    parser.add_argument(
        '--hatebu-address', dest='mail_to_addr',
        help=u'はてブ投稿用メールアドレス')
    parser.add_argument(
        '--from-address', dest='mail_from_addr',
        help=u'はてブへの送信元メールアドレス')
    parser.add_argument(
        '--gmail-username', dest='gmail_username',
        help=u'Gmailのユーザ名'
    )
    parser.add_argument(
        '--gmail-password', dest='gmail_password',
        help=u'Gmailのパスワード'
    )
    ns = parser.parse_args()
    config = parse_config(ns)
    for sec in ('delicious', 'mail'):
        for k, v in config[sec].items():
            if not v:
                raise parser.error(
                    '%s_%s doesnot exists.' % (sec.upper(), k.upper()))
    posts = fetch_posts(
        config['delicious']['username'],
        config['delicious']['password'],
        ns.offset)
    print(u'Got %s items' % len(posts))
    if posts:
        if config['gmail']['username'] and config['gmail']['password']:
            sendmail(
                config['mail']['from_addr'],
                config['mail']['to_addr'], posts,
                gmail_auth=(config['gmail']['username'],
                            config['gmail']['password']))
        else:
            sendmail(
                config['mail']['from_addr'],
                config['mail']['to_addr'], posts)


def parse_config(ns):
    """ パラメータを取得
    """
    if ns.config:
        filename = os.path.expanduser(ns.config)
    config = {
        'delicious': {'username': '', 'password': ''},
        'mail': {'from_addr': '', 'to_addr': ''},
        'gmail': {'username': '', 'password': ''}
    }
    parser = SafeConfigParser()
    if os.path.exists(filename):
        parser.read(filename)
    for sec in config:
        for opt in config[sec]:
            if parser.has_option(sec, opt):
                config[sec][opt] = parser.get(sec, opt)
            override = getattr(ns, '%s_%s' % (sec, opt))
            if override:
                config[sec][opt] = override
    return config


if __name__ == '__main__':
    command()
