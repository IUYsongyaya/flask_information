from flask import current_app
from flask import g
from flask import session, jsonify

from info import db
from info.models import User, News, Category
from info.utils.response_code import RET
from . import admin_blue
from flask import render_template, redirect, url_for, request
from info.utils.common import user_login_data
import time
from datetime import datetime, timedelta
from info.utils.image_storage import storage
from info import constants

@admin_blue.route("/add_category",methods = ["GET","POST"])
def add_category():
    cid = request.json.get("id")
    name = request.json.get("name")
    # 如果有id说明是修改标题
    # 如果没有id就说明是添加标题
    if cid:
       category = Category.query.get(cid)
       category.name = name
    else:

        category = Category()
        category.name = name
        db.session.add(category)

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="保存数据成功")



"""
新闻分类
"""
@admin_blue.route("/news_type")
def news_type():
    categorys = Category.query.all()
    category_list = []
    for category in categorys:
        category_list.append(category.to_dict())

    category_list.pop(0)
    return render_template("admin/news_type.html",data={"categories": category_list})




"""
编辑详情页面
"""


@admin_blue.route("/news_edit_detail", methods=["GET", "POST"])
def news_edit_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        news = News.query.get(news_id)
        categorys = Category.query.all()
        category_list = []
        for category in categorys:
            category_list.append(category.to_dict())

        category_list.pop(0)
        data = {
            "news": news.to_dict(),
            "categories": category_list
        }
        return render_template("admin/news_edit_detail.html", data=data)


    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    try:
        index_image = index_image.read()
        key = storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="第三方系统错误")

    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "ok")



"""
新闻编辑
"""


@admin_blue.route("/news_edit")
def news_edit():
    page = request.args.get("p", 1)
    keywords = request.args.get("keywords")
    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = News.query.order_by(News.create_time.desc()).paginate(page, 10, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    user_list = []
    for item in items:
        user_list.append(item.to_review_dict())

    data = {
        "news_list": user_list,
        "current_page": current_page,
        "total_page": total_page,
    }
    return render_template("admin/news_edit.html", data=data)


"""
新闻审核详情
"""


@admin_blue.route("/news_review_detail", methods=["GET", "POST"])
def news_review_detail():
    if request.method == "GET":
        news_id = request.args.get("news_id")
        news = News.query.get(news_id)
        data = {
            "news": news.to_dict()
        }
        return render_template("admin/news_review_detail.html", data=data)

    action = request.json.get("action")
    news_id = request.json.get("news_id")

    news = News.query.get(news_id)
    if action == "accept":
        # 表示通过
        news.status = 0
    else:
        # 拒绝的原因
        reason = request.json.get("reason")
        # 如果审核不通过,必须告诉我拒绝的原因
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        # 表示拒绝
        news.status = -1
        news.reason = reason

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="ok")


"""
新闻审核
"""


@admin_blue.route("/news_review")
def news_review():
    page = request.args.get("p", 1)
    keywords = request.args.get("keywords")
    try:
        page = int(page)
    except Exception as e:
        page = 1

    filter = [News.status != 0]
    if keywords:
        filter.append(News.title.contains(keywords))
    paginate = News.query.filter(*filter).order_by(News.create_time.desc()).paginate(page, 10, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    user_list = []
    for item in items:
        user_list.append(item.to_review_dict())

    data = {
        "news_list": user_list,
        "current_page": current_page,
        "total_page": total_page,
    }
    return render_template("admin/news_review.html", data=data)


"""
获取到所有注册用户的列表
"""


@admin_blue.route("/user_list")
def user_list():
    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(page, 10, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    user_list = []
    for item in items:
        user_list.append(item.to_admin_dict())

    data = {
        "users": user_list,
        "current_page": current_page,
        "total_page": total_page,
    }
    return render_template("admin/user_list.html", data=data)


"""
数据统计
"""


@admin_blue.route("/user_count")
def user_count():
    # 总人数
    total_count = 0
    # 每个月新增的人数
    mon_count = 0
    # 每天新增加的人数
    day_count = 0
    # 获取到总人数
    total_count = User.query.filter(User.is_admin == False).count()
    # 2018-08-01 00:00:00
    t = time.localtime()
    mon_begin = "%d-%02d-01" % (t.tm_year, t.tm_mon)
    mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')

    # 获取到本月的人数
    mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()

    # 2018-08-01 00:00:00
    t = time.localtime()
    day_begin = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')

    # 获取到今天的人数
    day_count = User.query.filter(User.is_admin == False, User.create_time >= day_begin_date).count()

    # 2018-08-01 00:00:00
    t = time.localtime()
    today_begin = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    today_begin_date = datetime.strptime(today_begin, '%Y-%m-%d')
    # 活跃用户
    active_count = []
    # 时间列表
    active_time = []
    for i in range(0, 30):
        # 获取今天开始时间
        begin_date = today_begin_date - timedelta(days=i)
        # 获取到结束时间
        end_date = today_begin_date - timedelta(days=(i - 1))
        # 获取到今天的人数
        count = User.query.filter(User.is_admin == False, User.create_time >= begin_date,
                                  User.create_time < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime('%Y-%m-%d'))

    active_count.reverse()
    active_time.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_time": active_time
    }

    return render_template("admin/user_count.html", data=data)


@admin_blue.route("/index")
@user_login_data
def admin_index():
    user = g.user
    return render_template("admin/index.html", user=user.to_dict())


@admin_blue.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        # 判断,如果用户已经登陆了,那么就不需要每次都登陆,
        if user_id and is_admin:
            return redirect(url_for("admin.admin_index"))
        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter(User.mobile == username, User.is_admin == True).first()

    if not user:
        return render_template("admin/login.html", errmsg="没有这个用户")

    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误")

    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = user.is_admin

    # 如果登陆成功,需要调到主页面
    return redirect(url_for("admin.admin_index"))
