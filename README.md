写在前面：本文只是开发的辅助文档，不是项目的说明文档, 项目的说明文档会在项目开发完成后编写。

## 项目说明
    这是沙河畔论坛的后端项目，使用Django框架开发，数据库使用MySQL，使用Django REST framework框架开发RESTful API接口。

## 开发环境
    Python 3.11.5
    Django 4.2.6
    MySQL 8.0.26

## 已完成的功能
- [x] 用户的注册、登录、注销
- [x] 用户的个人信息修改
- [x] 用户的密码修改
- [x] 用户的权限管理
- [x] 文章的增删改查与搜索
- 

## 待完成的功能
- [ ] 用户头像操作
- [ ] 用户邮箱验证
- [ ] 端到端加密
- [ ] 帖子封面操作
- [ ] 板块的相关操作
- [ ] 评论的相关操作
- [ ] 返回分页
- [ ] 点赞的相关操作
- [ ] 收藏的相关操作
- [ ] 通知的相关操作
- [ ] 前后端交接
- [ ] 功能优化, 持久化等
- [ ] 项目部署

## note
创建超级管理员    | python manage.py createsuperuser   
创建数据库表      | python manage.py makemigrations
应用数据库表      | python manage.py migrate
启动项目         | python manage.py runserver