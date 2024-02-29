from datetime import date
from flask import Flask,render_template,redirect,request,url_for,flash
from forms import LoginForm,SignupForm,SenOtp,NewPost,CommentForm,SearchForm,CreateThread
from send_otp import Sendmail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash,check_password_hash
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import uuid as uuid
import os
import random
from flask_gravatar import Gravatar
from flask_admin import Admin,AdminIndexView
from flask_admin.contrib.sqla import ModelView
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jfsdjfkjfkdjkfjdkjreieei4i4i4n4jn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = "static/images/"
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
db = SQLAlchemy(app)
ckeditor = CKEditor(app)
# gravatar
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
#login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Otp(db.Model):
    __tablename__ = "otp"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    email=db.Column(db.String(100),unique=True)
    verification_code=db.Column(db.Integer)

class Users(db.Model,UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    # relating with blog post
    posts = db.relationship("BlogPost", backref="poster")
    # *******Add parent relationship*******#
    # "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comments", back_populates="comment_author")
    # relation with thread post
    thread_posts = relationship("Thread", back_populates="thread_author")
    # relation with Threadcomment1
    thread_comments_one = relationship("ThreadCommentsOne", back_populates="thread_comment_author")
    # relation with threadcommment2
    thread_comments_two = relationship("ThreadCommentsTwo", back_populates="thread_comment_two_author")

class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), nullable=False,unique=True)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pic = db.Column(db.String,nullable=True)
    # poster id
    # creating foreignkey refer to the primary key of the user
    poster_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    # ***************Parent Relationship*************#
    comments = relationship("Comments", back_populates="parent_post")

class Comments(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer,primary_key=True)
    #adding user child relationship
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("Users", back_populates="comments")

    #adding blogpost relationship
    # ***************Child Relationship*************#
    post_id = db.Column(db.Integer, db.ForeignKey("blog_post.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class Thread(db.Model):
    __tablename__="thread"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(250),nullable=False)
    brief = db.Column(db.String(250),nullable=False)
    categories = db.Column(db.String(250),nullable=True)
    hashtags = db.Column(db.String(250),nullable=True)
    date = db.Column(db.String(250),nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    thread_author = relationship("Users", back_populates="thread_posts")
    # relation with thread comments
    thread_comments = relationship("ThreadCommentsOne", back_populates="parent_thread")

# class ThreadComments1(db.Model):
#     __tablename__="thread_comments1"
#     id = db.Column(db.Integer,primary_key=True)
#     author_id = db.Column(db.Integer,db.ForeignKey("users.id"))
#     thread_id = db.Column(db.Integer,db.ForeignKey("threads.id"))
#     text = db.Column(db.Text,nullable=False)

class ThreadCommentsOne(db.Model):
    __tablename__ = "thread_comments_one"
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.String(250), nullable=False)
    thread_comment_author = relationship("Users", back_populates="thread_comments_one")

    thread_id = db.Column(db.Integer, db.ForeignKey("thread.id"))
    parent_thread = relationship("Thread", back_populates="thread_comments")
    text = db.Column(db.Text,nullable=False)

    thread_comments_two = relationship("ThreadCommentsTwo", back_populates="thread_comment")


class ThreadCommentsTwo(db.Model):
    __tablename__ = "thread_comments_two"
    id = db.Column(db.Integer,primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.String(250), nullable=False)
    thread_comment_two_author = relationship("Users", back_populates="thread_comments_two")

    thread_comment_one_id = db.Column(db.Integer, db.ForeignKey("thread_comments_one.id"))
    thread_comment = relationship("ThreadCommentsOne", back_populates="thread_comments_two")

    text = db.Column(db.Text, nullable=False)


class ReportCommentsOne(db.Model):
    __tablename__ = "report_comments_one"
    id = db.Column(db.Integer,primary_key=True)
    comment_id = db.Column(db.Integer)
    reported_user = db.Column(db.Integer)

class ReportCommentsTwo(db.Model):
    __tablename__ = "report_comments_two"
    id = db.Column(db.Integer,primary_key=True)
    comment_id = db.Column(db.Integer)
    reported_user = db.Column(db.Integer)

#admin
class MyIndexAdminView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.email == "vigneshrauvk13@gmail.com":
                return True


admin=Admin(app,index_view=MyIndexAdminView())
class MyModelView(ModelView):
    page_size = 5;
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.email == "vigneshrauvk13@gmail.com":
                return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login",next=request.url))

admin.add_view(MyModelView(Users,db.session))
admin.add_view(MyModelView(BlogPost,db.session))
admin.add_view(MyModelView(Comments,db.session))
admin.add_view(MyModelView(Thread,db.session))
admin.add_view(MyModelView(ThreadCommentsOne,db.session))
admin.add_view(MyModelView(ThreadCommentsTwo,db.session))
admin.add_view(MyModelView(ReportCommentsOne,db.session))
admin.add_view(MyModelView(ReportCommentsTwo,db.session))
admin.add_view(MyModelView(Otp,db.session))




# search
@app.context_processor
def inject_data():
    search_form = SearchForm()
    return dict(search_form=search_form)


@app.route('/')
def index():  # put application's code here
    db.create_all()
    posts = BlogPost.query.all()
    posts.reverse()
    return render_template("index.html",all_post=posts,current_user=current_user)


@app.route("/signup",methods=["POST","GET"])
def signup():
    send_otp = SenOtp()
    if send_otp.validate_on_submit():
        name = send_otp.name.data;
        email = send_otp.email.data;
        existing_user = Users.query.filter_by(email=email).first()
        existing_user_in_otp = Otp.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exist ")
            return redirect(url_for("login"))
        elif existing_user_in_otp:
            flash("OTP has already sent to your mail")
            return redirect(url_for("create_account",
                                    value_name=name,
                                    value_email=email))
        else:
            verification_code = random.randint(1000, 9999)
            send = Sendmail()
            send.mail(email, name, verification_code)
            new_user = Otp(username=name,
                           email=email,
                           verification_code=verification_code)

            db.session.add(new_user)
            db.session.commit()
            flash("OTP sent to your mail")
            return redirect(url_for("create_account",
                                    value_name=name,
                                    value_email=email))

    return render_template("signup.html",send_otp=send_otp)

@app.route("/create_account",methods=["POST","GET"])
def create_account():
    form = SignupForm()
    value_name = request.args["value_name"]
    value_email = request.args["value_email"]
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        otp = form.opt.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        print(name, email, otp, password, confirm_password)
        otp_user_data = Otp.query.all()
        for data in otp_user_data:
            if data.email == email:
                if data.username == name and data.verification_code == int(otp) and password == confirm_password:
                    hash_and_salt_password = generate_password_hash(password=password,method="pbkdf2:sha256",salt_length=8)
                    new_user = Users(email=email,password=hash_and_salt_password,name=name)
                    db.session.add(new_user)
                    db.session.commit()
                    required_user_after_otp = Otp.query.filter_by(email=email).first()
                    db.session.delete(required_user_after_otp)
                    db.session.commit()
                    flash("Your account has been created successfully! please login")
                    return redirect(url_for("login"))
                elif password != confirm_password:
                    flash("Password does not match")
                elif data.username != name or data.email != email:
                    flash("Check your username and email")
                elif data.verification_code != otp:
                    flash("Enter correct OTP")


    return render_template("create_account.html",form=form,value_name=value_name,value_email=value_email)



@app.route("/login",methods=["POST","GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(email,password)
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            if check_password_hash(existing_user.password,password):
                login_user(existing_user)
                return redirect(url_for("index"))
            else:
                flash("Wrong password")
        else:
            flash("User doesn't exist ")

    return render_template("login.html",form=form)



@app.route("/new_post",methods=["POST","GET"])
@login_required
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        # handling picture
        pic = form.pic.data
        if pic!=None:
            pic_file_name = secure_filename(pic.filename)
            unique_pic_name = str(uuid.uuid1()) + "_" + pic_file_name
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_pic_name))
        else:
            unique_pic_name = "no-image.png"
        #checking slug
        slug = form.slug.data
        existing_slug = BlogPost.query.filter_by(slug=slug).first()
        if existing_slug:
            flash("slug is already exist.Please enter unique slug")
        else:
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                slug=form.slug.data,
                body=form.body.data,
                date=date.today().strftime("%B %d, %Y"),
                pic=unique_pic_name,
                poster_id=current_user.id
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("new_post.html",form=form)

@app.route("/post/<string:slug>",methods=["POST","GET"])
def show_post(slug):
    form = CommentForm()
    required_post = BlogPost.query.filter_by(slug=slug).first()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        new_comment = Comments(
                        text=form.comment_text.data,
                        comment_author=current_user,
                        parent_post=required_post
                     )
        db.session.add(new_comment)
        db.session.commit()

    return render_template("post.html",post=required_post,form=form,current_user=current_user)


@app.route("/post_comment/delete/<int:id>",methods=["GET"])
@login_required
def post_comment_delete(id):
    required_comment = Comments.query.filter_by(id=id).first()
    if current_user.id == required_comment.author_id:
        db.session.delete(required_comment)
        db.session.commit()
    required_post = BlogPost.query.filter_by(id=required_comment.post_id).first();
    return redirect(url_for("show_post",slug=required_post.slug))



@app.route("/dashboard",methods=["POST","GET"])
@login_required
def dashboard():
    print(current_user.id)
    user = Users.query.filter_by(id=current_user.id).first()
    # print(all_post.posts[0].title)
    return render_template("dashboard.html",user=user)

@app.route("/logout",methods=["POST","GET"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect(url_for("login"))

@app.route("/delete/<string:slug>",methods=["POST","GET"])
@login_required
def delete_post(slug):
    required_post = BlogPost.query.filter_by(slug=slug).first()
    #print(required_post.title)
    if required_post.poster_id == current_user.id:
        #print(True,required_post.poster_id,current_user.id)
        if required_post.pic != "no-image.png":
            os.remove(os.path.join(UPLOAD_FOLDER, required_post.pic))
        db.session.delete(required_post)
        db.session.commit()
        #  delete comments
        all_comments =Comments.query.all()
        for comment in all_comments:
            #print(comment.post_id)
            if comment.post_id == None:
                db.session.delete(comment)
                db.session.commit()
    else:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/edit_post/<string:slug>",methods=["POST","GET"])
@login_required
def edit_post(slug):
    required_post = BlogPost.query.filter_by(slug=slug).first()
    edit_form = NewPost(
            title=required_post.title,
            subtitle=required_post.subtitle,
            slug=required_post.slug,
            body=required_post.body,

    )
    if edit_form.validate_on_submit():
        pic = edit_form.pic.data
        if pic!=None:
            pic_file_name = secure_filename(pic.filename)
            unique_pic_name = str(uuid.uuid1()) + "_" + pic_file_name
            pic.save(os.path.join(UPLOAD_FOLDER, unique_pic_name))
            #  saving in data base
            required_post.pic= unique_pic_name
        required_post.title = edit_form.title.data
        required_post.subtitle = edit_form.subtitle.data
        required_post.slug=edit_form.slug.data;
        required_post.body=edit_form.body.data;
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("new_post.html",form=edit_form,current_user=current_user)


@app.route("/search",methods=["POST"])
def search():
    search_form = SearchForm()
    if search_form.validate_on_submit():
        searched_data = search_form.search.data;
        # search database
        searched_posts = BlogPost.query.filter(BlogPost.title.like("%"+searched_data+"%"))
        searched_posts.order_by(BlogPost.title).all()
        return render_template("search.html",searched_posts=searched_posts)

@app.route("/discussion",methods=["GET","POST"])
def discussion():
    threads = Thread.query.all()
    threads.reverse()
    return render_template("forum_index.html",all_threads=threads)

@app.route("/discussion/filter_by",methods=["GET","POST"])
def discussion_filter():
    if request.args["categories"] == "general" and request.args["sort_by"] == "old":
        print(request.args["categories"], request.args["sort_by"])
        required_thread = Thread.query.filter_by(categories="general").all()
        return render_template("forum_index.html", all_threads=required_thread, categories="general")
    elif request.args["sort_by"] == "replys" and request.args["categories"] == "general":
        threads = Thread.query.filter(Thread.thread_comments).all()
        required_threads =[]
        for thread in threads:
            if thread.categories == "general":
                required_threads.append(thread)
        return render_template("forum_index.html", all_threads=required_threads)
    elif request.args["categories"] == "general":
        print("working")
        required_thread = Thread.query.filter_by(categories="general").all()
        required_thread.reverse()
        return render_template("forum_index.html", all_threads=required_thread, categories="general")

    elif request.args["categories"] == "Sports" and request.args["sort_by"] == "old":
        required_thread = Thread.query.filter_by(categories="Sports").all()
        return render_template("forum_index.html", all_threads=required_thread, categories="Sports")
    elif request.args["sort_by"] == "replys" and request.args["categories"] == "Sports":
        threads = Thread.query.filter(Thread.thread_comments).all()
        required_threads =[]
        for thread in threads:
            if thread.categories == "Sports":
                required_threads.append(thread)
        return render_template("forum_index.html", all_threads=required_threads)
    elif request.args["categories"] == "Sports":
        required_thread = Thread.query.filter_by(categories="Sports").all()
        required_thread.reverse()
        return render_template("forum_index.html", all_threads=required_thread, categories="Sports")

    elif request.args["categories"] == "Education" and request.args["sort_by"] == "old":
        required_thread = Thread.query.filter_by(categories="Education").all()
        return render_template("forum_index.html", all_threads=required_thread, categories="Education")
    elif request.args["sort_by"] == "replys" and request.args["categories"] == "Education":
        threads = Thread.query.filter(Thread.thread_comments).all()
        required_threads =[]
        for thread in threads:
            if thread.categories == "Education":
                required_threads.append(thread)
        return render_template("forum_index.html", all_threads=required_threads)
    elif request.args["categories"] == "Education":
        required_thread = Thread.query.filter_by(categories="Education").all()
        required_thread.reverse()
        return render_template("forum_index.html", all_threads=required_thread, categories="Education")

    elif request.args["sort_by"] == "latest" and request.args["categories"] == "":
        threads = Thread.query.all()
        threads.reverse()
        return render_template("forum_index.html", all_threads=threads)
    elif request.args["sort_by"] == "old" and request.args["categories"] == "":
        threads = Thread.query.all()
        return render_template("forum_index.html", all_threads=threads)



    elif request.args["sort_by"] == "replys" and request.args["categories"] == "":
        threads = Thread.query.filter(Thread.thread_comments).all()
        print(threads)
        return render_template("forum_index.html", all_threads=threads)



@app.route("/create_forum",methods=["GET","POST"])
@login_required
def create_forum():
    is_deletable = False
    form = CreateThread()
    if form.validate_on_submit():
        hash_tags=""
        tags = form.hashtags.data.split(",")
        for tag in tags:
            hash_tags=hash_tags+"#"+tag
        new_thread = Thread(
            title=form.title.data,
            brief=form.brief.data,
            categories=form.categories.data,
            hashtags=hash_tags,
            date=date.today().strftime("%B %d, %Y"),
            thread_author=current_user
        )
        db.session.add(new_thread)
        db.session.commit()
        return redirect(url_for("discussion"))
    return render_template("new_forum.html",form=form,is_deletable=is_deletable)

@app.route("/discussion/<int:thread_id>/<string:thread>",methods=["GET","POST"])
def show_thread(thread,thread_id):
    required_thread = Thread.query.filter_by(id=thread_id).first()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please login before reply")
            return redirect(url_for("login"))
        new_comment1 = ThreadCommentsOne(
            text=form.comment_text.data,
            date=date.today().strftime("%B %d, %Y"),
            thread_comment_author=current_user,
            parent_thread=required_thread
        )
        db.session.add(new_comment1)
        db.session.commit()

    return render_template("thread_post.html",thread=required_thread,form=form)


@app.route("/discussion/<string:thread>/<int:comment>",methods=["GET","POST"])
def show_thread_comments(thread,comment):
    required_thread_comment = ThreadCommentsOne.query.filter_by(id=comment).first()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please login before reply")
            return redirect(url_for("login"))
        new_comment2 = ThreadCommentsTwo(
            text=form.comment_text.data,
            date=date.today().strftime("%B %d, %Y"),
            thread_comment_two_author=current_user,
            thread_comment=required_thread_comment

        )
        db.session.add(new_comment2)
        db.session.commit()
    return render_template("second_level_thread.html",thread_comment=required_thread_comment,form=form)

@app.route("/discussion/edit",methods=["GET","POST"])
@login_required
def edit_thread():
    is_deletable = True
    thread_id = request.args["thread_id"]
    print(type(thread_id))
    required_thread = Thread.query.filter_by(id=thread_id).first()
    tags = required_thread.hashtags.split("#")
    hash_tags = ""
    for tag in tags:
        hash_tags = hash_tags + "," + tag
    edit_thread = CreateThread(
        title=required_thread.title,
        brief=required_thread.brief,
        categories=required_thread.categories,
        hashtags=hash_tags[2:]
    )
    if edit_thread.validate_on_submit():
        hash_tags = ""
        tags = edit_thread.hashtags.data.split(",")
        for tag in tags:
            hash_tags = hash_tags + "#" + tag
        required_thread.title=edit_thread.title.data
        required_thread.brief=edit_thread.brief.data
        required_thread.categories=edit_thread.categories.data
        required_thread.hashtags=hash_tags
        db.session.commit()
        return redirect(url_for("show_thread",thread_id=required_thread.id,thread=required_thread.title))
    return render_template("new_forum.html",form=edit_thread,is_deletable=is_deletable,required_thread_id=required_thread.id)

@app.route("/discussion/delete/<int:thread_id>",methods=["GET","POST"])
@login_required
def delete_thread(thread_id):
    required_thread = Thread.query.filter_by(id=thread_id).first()
    if required_thread.author_id == current_user.id:
        db.session.delete(required_thread)
        db.session.commit()
        # deleting threadcomments 1
        all_threadcommentsone = ThreadCommentsOne.query.all()
        for comment in all_threadcommentsone:
            if comment.thread_id is None:
                db.session.delete(comment)
                db.session.commit()
        all_threadcommentstwo = ThreadCommentsTwo.query.all()
        for comment in all_threadcommentstwo:
            if comment.thread_comment_one_id is None:
                db.session.delete(comment)
                db.session.commit()

    return redirect(url_for("discussion"))

@app.route("/discussion/comment/edit/<int:thread_id>/<int:comment_id>",methods=["GET","POST"])
@login_required
def edit_comment_one(thread_id,comment_id):
    required_thread = Thread.query.filter_by(id=thread_id).first()
    required_comment = ThreadCommentsOne.query.filter_by(id=comment_id).first()
    form = CommentForm(comment_text=required_comment.text)
    if form.validate_on_submit():
        required_comment.text = form.comment_text.data
        db.session.commit()
        return redirect(url_for("show_thread",thread_id=required_thread.id,thread=required_thread.title))
    return render_template("edit_thread_command.html", thread=required_thread, form=form,required_comment=required_comment)

@app.route("/discussion/comment/delete/<int:thread_id>/<int:comment_id>",methods=["GET"])
@login_required
def delete_comment_one(comment_id,thread_id):
    required_thread = Thread.query.filter_by(id=thread_id).first()
    required_comment = ThreadCommentsOne.query.filter_by(id=comment_id).first()
    if current_user.id == required_comment.author_id:
        db.session.delete(required_comment)
        db.session.commit()
        all_threadcommentstwo = ThreadCommentsTwo.query.all()
        for comment in all_threadcommentstwo:
            if comment.thread_comment_one_id is None:
                db.session.delete(comment)
                db.session.commit()
        return redirect(url_for("show_thread", thread_id=required_thread.id, thread=required_thread.title))

@app.route("/discussion/comment_two/edit/<int:comment>/<int:comment_two>",methods=["GET","POST"])
@login_required
def edit_comment_two(comment,comment_two):
    required_thread_comment = ThreadCommentsOne.query.filter_by(id=comment).first()
    required_thread_comment_two = ThreadCommentsTwo.query.filter_by(id=comment_two).first()
    form = CommentForm(comment_text=required_thread_comment_two.text)
    if form.validate_on_submit():
        required_thread_comment_two.text = form.comment_text.data
        db.session.commit()
        return redirect(url_for("show_thread_comments",thread=required_thread_comment.parent_thread.title,comment=required_thread_comment.id))
    return render_template("edit_second_level_thread.html", thread_comment=required_thread_comment, form=form,comment_two=required_thread_comment_two)

@app.route("/discussion/comment_two/delete/<int:comment>/<int:comment_two>",methods=["GET"])
@login_required
def delete_comment_two(comment,comment_two):
    required_thread_comment = ThreadCommentsOne.query.filter_by(id=comment).first()
    required_thread_comment_two = ThreadCommentsTwo.query.filter_by(id=comment_two).first()
    if current_user.id == required_thread_comment_two.author_id:
        db.session.delete(required_thread_comment_two)
        db.session.commit()
        return redirect(url_for("show_thread_comments", thread=required_thread_comment.parent_thread.title,
                                comment=required_thread_comment.id))


@app.route("/discussion/report/comment1/<int:comment_id>",methods=["GET"])
@login_required
def report_comment1(comment_id):
    report = ReportCommentsOne.query.all();
    is_reported = False
    if len(report) == 0:
        new_report = ReportCommentsOne(
            comment_id=comment_id,
            reported_user=current_user.id
        )
        db.session.add(new_report)
        db.session.commit()
        flash("successfully reported")
    else:
        for data in report:
            print(data.comment_id,data.reported_user)
            if data.reported_user == current_user.id and data.comment_id == comment_id:
                flash("already reported")
                is_reported = True

        if not is_reported:
            new_report = ReportCommentsOne(
                comment_id=comment_id,
                reported_user=current_user.id
            )
            db.session.add(new_report)
            db.session.commit()
            comments = ReportCommentsOne.query.filter_by(comment_id=comment_id).all()
            flash("successfully reported")
            if len(comments) > 1:
                # deleting comment
                comments_one = ThreadCommentsOne.query.filter_by(id=comment_id).first()
                db.session.delete(comments_one)
                db.session.commit()
                all_threadcommentstwo = ThreadCommentsTwo.query.all()
                for comment in all_threadcommentstwo:
                    if comment.thread_comment_one_id is None:
                        db.session.delete(comment)
                        db.session.commit()
                # deleting report
                for comment in comments:
                    db.session.delete(comment)
                    db.session.commit()
    return redirect(request.referrer)

@app.route("/discussion/report/comment2/<int:comment_id>",methods=["GET"])
def report_comment_two(comment_id):
    report = ReportCommentsTwo.query.all();
    is_reported = False
    if len(report) == 0:
        new_report = ReportCommentsTwo(
            comment_id=comment_id,
            reported_user=current_user.id
        )
        db.session.add(new_report)
        db.session.commit()
        flash("Successfully reported")
    else:
        for data in report:
            if data.comment_id == comment_id and data.reported_user == current_user.id:
                flash("Already reported")
                is_reported = True
        if not is_reported:
            new_report = ReportCommentsTwo(
                comment_id=comment_id,
                reported_user=current_user.id
            )
            db.session.add(new_report)
            db.session.commit()
            flash("successfully reported")

            comments = ReportCommentsTwo.query.filter_by(comment_id=comment_id).all()
            if len(comments) > 1:
                required_thread_comment_two = ThreadCommentsTwo.query.filter_by(id=comment_id).first()
                db.session.delete(required_thread_comment_two)
                db.session.commit()
                # deleting report
                for comment in comments:
                    db.session.delete(comment)
                    db.session.commit()
    return redirect(request.referrer)




if __name__ == '__main__':
    app.run(debug=True)
