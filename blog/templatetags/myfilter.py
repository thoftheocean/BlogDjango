#coding:utf-8
from django import template
import datetime
register = template.Library()

# 定义一个将日期中的月份转换为大写的过滤器，如8转换为八
@register.filter
def month_to_upper(key):
    print 'this is key', key
    return ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'][key.month-1]

# 注册过滤器
# register.filter('month_to_upper', month_to_upper)

@register.filter()
def time_before(d):
    # if isinstance(d, str):
    #         d = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()
    d = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
    now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

    # print('创建时间', d, type(d))
    # print('当前时间', now, type(now))
    delta = (now-d)
    before = delta.days * 24 * 60 * 60 + delta.seconds
    # print('过去了多少秒', before)

    chunks = (
    (60 * 60 * 24 * 365, u'年'),
    (60 * 60 * 24 * 30, u'月'),
    (60 * 60 * 24 * 7, u'周'),
    (60 * 60 * 24, u'天'),
    (60 * 60, u'小时'),
    (60, u'分钟'),
    (1, u'秒'),
    )
    if before < 60:
        return u'刚刚'
    for seconds, unit in chunks:
        count = before // seconds
        if count != 0:
            break

    return (str(count) + unit + u"前发布")