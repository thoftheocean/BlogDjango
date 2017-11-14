# -*- coding:utf-8 -*-
# from django.contrib import admin
import xadmin
from xadmin import views

from models import *

# Register your models here.
# 基本的修改
class BaseSetting(object):
    enable_themes = True   # 打开主题功能
    use_bootswatch = True  #

# 针对全局的
class GlobalSettings(object):
    site_title = "博客后台管理系统"  # 系统名称
    site_footer = "T博客在线"      # 底部版权栏
    menu_style = "accordion"     # 将菜单栏收起来


class UserAdmin(object):
    list_display = ['username', 'mobile']

class ArticleAdmin(object):

    list_display = ('title', 'desc', 'category', 'click_count',)
    list_display_links = ('title', 'desc')
    list_editable = ('click_count',)

    fieldsets = (
        (None, {
            'fields': ('title', 'desc', 'content', 'user', 'category', 'tag', )
        }),
        ('高级设置', {
            'classes': ('collapse',),
            'fields': ('click_count', 'is_recommend',)
        }),
    )

    #增加富文本编辑器
    class Media:
        js = (
            '/static/js/kindeditor/kindeditor-min.js',
            '/static/js/kindeditor/lang/zh_CN.js',
            '/static/js/kindeditor/config.js',
        )

# 注册，注意一个是BaseAdminView，一个是CommAdminView
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)


# xadmin.site.register(User,UserAdmin)
xadmin.site.register(Tag)
xadmin.site.register(Article, ArticleAdmin)
xadmin.site.register(Category)
xadmin.site.register(Comment)
xadmin.site.register(Links)
xadmin.site.register(Advertisement)

