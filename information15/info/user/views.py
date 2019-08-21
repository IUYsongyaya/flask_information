from info import constants
from info import db
from info.models import Category, News
from info.utils.response_code import RET
from . import user_blue
from flask import render_template,g,redirect,request,jsonify
from info.utils.common import user_login_data
from info.utils.image_storage import storage

@user_blue.route("/news_list")
@user_login_data
def news_list():
    user = g.user
    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = News.query.filter(News.user_id == user.id).paginate(page, 2, False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    items_list = []
    for item in items:
        items_list.append(item.to_review_dict())

    data = {
        "news_list": items_list,
        "current_page": current_page,
        "total_page": total_page
    }
    return render_template("news/user_news_list.html", data=data)



@user_blue.route("/news_release",methods = ["GET","POST"])
@user_login_data
def news_release():
    user = g.user
    if request.method == "GET":
        categorys = Category.query.all()
        category_list = []
        for category in categorys:
            category_list.append(category.to_dict())
        category_list.pop(0)
        data = {
            "categories":category_list
        }
        return render_template("news/user_news_release.html",data = data)

        # 1. 获取要提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image").read()
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")


    key = storage(index_image)

    news = News()
    news.title = title
    news.source = source
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = user.id
    news.status = 1

    db.session.add(news)
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "发布成功")







@user_blue.route("/collection")
@user_login_data
def collection():
    user = g.user
    page = request.args.get("p",1)

    try:
        page = int(page)
    except Exception as e:
        page = 1

    paginate = user.collection_news.paginate(page,2,False)
    items = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    items_list = []
    for item in items:
        items_list.append(item.to_review_dict())

    data = {
       "collections":items_list,
       "current_page":current_page,
       "total_page":total_page
    }
    return render_template("news/user_collection.html",data = data)






@user_blue.route("/pass_info",methods = ["GET","POST"])
@user_login_data
def pass_info():
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/user_pass_info.html", data=data)

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not user.check_password(old_password):
        return jsonify(errno = RET.PWDERR,errmsg = "密码错误")

    user.password = new_password
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "密码修改成功")




@user_blue.route("/pic_info",methods = ["GET","POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/user_pic_info.html",data = data)

    #  获取到用户传递过来的头像参数
    avatar_url = request.files.get("avatar").read()
    # 在传递到七牛之后,七牛会返回一个key,返回的目的是帮助我们取访问图片
    key = storage(avatar_url)

    user.avatar_url = key
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "头像设置成功",data={"avatar_url": constants.QINIU_DOMIN_PREFIX + key})




@user_blue.route("/base_info",methods = ["GET","POST"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":

        data = {
            "user_info": user.to_dict() if user else None,
        }
        return render_template("news/user_base_info.html",data = data)

    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name,signature,gender]):
        return jsonify(errno = RET.PARAMERR,errmsg = "请输入正确的参数")

    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "ok")



@user_blue.route("/info")
@user_login_data
def get_user_info():
    user = g.user
    if not user:
        return redirect("/")
    data = {
        "user_info": user.to_dict() if user else None,
    }
    return render_template("news/user.html",data = data)
