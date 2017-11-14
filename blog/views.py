#coding:utf-8
from django.shortcuts import render, redirect, HttpResponse
from models import *
import logging
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage,EmptyPage,PageNotAnInteger
from django.db.models import Count
from forms import *
import json


logger = logging.getLogger('blog.views')

#全局数据
def global_setting(request):
    #站点基本信息
    SITE_URL = settings.SITE_URL,
    SITE_NAME = settings.SITE_NAME,
    SITE_DESC = settings.SITE_DESC,
    WEIBO_SINA = settings.WEIBO_SINA,
    WEIBO_TENCENT = settings.WEIBO_TENCENT,
    PRO_RSS = settings.PRO_RSS,
    PRO_EMAIL= settings.PRO_EMAIL,
    #分类信息数据
    category_list = Category.objects.all()
    #文章归档数据
    archive_list = Article.objects.distinct_date_list()
    #广告数据

    #标签云数据
    tag_list = Tag.objects.all()

    #友情链接数据
    link_list = Links.objects.all()
    #文章排行榜数据

    #浏览排行
    article_click_list = Article.objects.all().order_by('-click_count')[0:5]

    #评论排行
    comment_count_list = Comment.objects.values('article').annotate(comment_count=Count('article')).order_by('-comment_count')
    article_comment_list = [Article.objects.get(pk=comment_count['article'])for comment_count in comment_count_list]
    article_comment_list = article_comment_list[0:5]


    #站长推荐
    recommend_list = Article.objects.all().order_by('-is_recommend')[0:5]


    return locals()
#首页
def index(request):
    try:
        #分页器和文章显示
        article_list = Article.objects.all()
        article_list = getPage(request, article_list)



        #文章归档
        #获取文章中的年份-月份,distinct()对整个字段进行重复
        # from django.db import connection
        # cursor = connection.cursor()
        # cursor.execute("SELECT DISTINCT DATE_FORMAT(date_publish, '%Y-%m') as col_date FROM blog_article ORDER BY date_publish")
        # row = cursor.fetchall()
        # print row
    except Exception as e:
        logger.error(e)
    return render(request, 'index.html', locals())

def archive(request):
    try:
        #获取客户端提交的信息
        year = request.GET.get('year', None)
        month = request.GET.get('month', None)
        print '年份:',year,'月份：',month
        article_list = Article.objects.filter(date_publish__icontains=year + '-' + month)
        article_list = getPage(request,article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'archive.html', locals())


#分页代码
def getPage(request,article_list):
    paginator = Paginator(article_list, 5)  # 数字决定每页显示的数目。
    try:
        page = int(request.GET.get('page', 1))  # 没有page变量时，默认值为1
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list

#标签
def tag(requst):
    pass

# 文章详情
def article(request):
    try:
        # 获取文章id
        id = request.GET.get('id', None)
        try:
            # 获取文章信息
            article = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})
        #增加点击数
        # click_count = article.click_count +1
        # Article.objects.create(click_count=click_count).save()
        # print Article.objects.get(pk=id).click_count

        #文章评论数

        comment_count=Comment.objects.filter(article_id=id).annotate(comment_count=Count('comment'))

        # 评论表单实例化
        comment_form = CommentForm({'article': id} if request.user.is_authenticated() else{'article': id})

        # 获取评论信息
        comments = Comment.objects.filter(article=article).order_by('id')
        comment_list = []
        for comment in comments:
            for item in comment_list:
                if not hasattr(item, 'children_comment'):
                    setattr(item, 'children_comment', [])
                if comment.pid == item:
                    item.children_comment.append(comment)
                    break
            if comment.pid is None:
                comment_list.append(comment)
    except Exception as e:
        print e
        logger.error(e)
    return render(request, 'article.html', locals())

# 提交评论
def comment_post(request):
    print '提交评论'
    try:
        comment_form = CommentForm(request.POST)
        #验证用户是否登录
        if comment_form.is_valid():
            #获取表单信息
            comment = Comment.objects.create(
                                            comment_user=request.user,
                                            content=comment_form.cleaned_data["comment"],
                                            article_id=comment_form.cleaned_data["article"],
                                             )
            comment.save()
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])

# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():

                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                    email=reg_form.cleaned_data["email"],
                                    url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),)
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(request, user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'reg.html', locals())

# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())

def category(request):
    try:
        # 先获取客户端提交的信息

        category= request.GET.get('category', None)
        try:
            article_list = Article.objects.filter(category__name=category)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '分类不存在'})
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())

