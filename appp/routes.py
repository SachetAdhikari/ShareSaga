import os
import secrets
from PIL import Image
from flask import render_template,url_for,flash,redirect,request, abort, send_file,session
from appp import app,db, bcrypt, mail, oauth
from appp.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm,
                        ContributeResourcesForm, AddCourseForm, DeleteCourseForm, AddBatchForm, RequestResetForm, ResetPasswordForm, CommentForm)
from appp.models import Users, Post, Resources, Courses, BatchChoices, Comment
from flask_login import login_user, current_user, logout_user,login_required
from flask_mail import Message
import re
import time

@app.route("/")
@app.route("/home")
def home():
    page=request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=7)
    return render_template('home.html',posts=posts,title="Home")

@app.route("/about")
def about():
    return render_template('about.html',title="About")



def save_facultypic(facultypic,course,batch,facultyname):
    _ , f_ext = os.path.splitext(facultypic.filename)
    pic_fn = batch+ course+ facultyname + f_ext
    pic_path= os.path.join(app.root_path,'static/faculty_pics',pic_fn)
    
    output_size = (125,125)
    i=Image.open(facultypic)
    i.thumbnail(output_size)
    i.save(pic_path)
    return pic_fn

@app.route("/shareSaga2020/admin",methods=['GET','POST'])
@login_required
def admin():
    if (current_user.fullname==os.environ.get('MASTERUSER')) and (current_user.email==os.environ.get('MASTEREMAIL')):
        formA= AddCourseForm()
        formD= DeleteCourseForm()
        formB= AddBatchForm()
        if formA.course.data:
            if formA.fpic.data:
                facultyPic= save_facultypic(formA.fpic.data,formA.course.data,formA.batch.data,formA.fname.data)
                add=Courses(course=formA.course.data,batch=formA.batch.data,faculty_name=formA.fname.data,faculty_pic=facultyPic)
                db.session.add(add)
                db.session.commit()
            else:
                add=Courses(course=formA.course.data,batch=formA.batch.data,faculty_name=formA.fname.data)
                db.session.add(add)
                db.session.commit()
            flash(f'Course {formA.course.data} has been added!','success')
            return redirect(url_for('admin'))
        if formD.coursee.data:
            remove= Courses.query.filter(Courses.course.contains(formD.coursee.data), Courses.batch.contains(formD.batch.data)).first()
            if remove:
                db.session.delete(remove)
                db.session.commit()
                flash(f'Course {formD.coursee.data} has been removed!','info')
            else:
                flash('No such course found!','info')
            return redirect(url_for('admin'))

        if formB.available_batch.data:
            batch= formB.available_batch.data
            add_batch= BatchChoices(batch=batch)
            db.session.add(add_batch)
            db.session.commit()
            flash(f"Batch {batch} has been added!",'success')
            return redirect(url_for('admin'))

        return render_template('admin.html',title='Admin Panel',formA=formA,formD=formD,formB=formB)
    else:
        abort(403)


@app.route('/completeSignup',methods=['GET','POST'])
def completeSignup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    profile = dict(session).get('profile',None)
    email=profile['email']
    fullname=profile['given_name']
    vregno=profile['family_name']

    ev= bool(re.findall("(@vitstudent.ac.in)$",email))
    if not ev:
        flash(f"Please use VIT email to register! You can try logging of current google account from your brower and try logging in with VIT email!",'info')
        return redirect(url_for('register'))
    else:
        ev2=bool(re.findall("(2019@vitstudent.ac.in)$",email))
        if not ev2:
            flash(f"Hi VITian! We currently support '2019@vitstudent.ac.in'. We will soon expand to all VITians. Sorry for your inconvenience! ",'info')
            return redirect(url_for('register'))


    user = Users.query.filter_by(email=email).first()
    if user:
        flash(f"An account for {email} is already created. Please try a different one!",'info')
        return redirect(url_for('login'))


    form= RegistrationForm()
    if form.validate_on_submit():
        hashed_password =bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=Users(fullname=fullname,email=email,vregno=vregno,batch=form.batch.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        session.pop('profile')
        flash(f'Account created for {vregno}! You can now login!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html',title="Sign Up", form=form)

@app.route('/signup')
def signupwithGoogle():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    user = oauth.google.userinfo()
    session['profile'] = user_info
    return redirect(url_for('completeSignup'))





@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('register.html',title="Sign Up")

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form= LoginForm()
    if form.validate_on_submit():
        VREGNO=(form.vregno.data).upper()
        user= Users.query.filter_by(vregno=VREGNO).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You are logged in as {VREGNO}!', 'success')
            return redirect (next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsucccessful. Please check your VIT Registration No and Password!', 'danger')
    return render_template('login.html',title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex= secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn =random_hex + f_ext
    picture_path= os.path.join(app.root_path,'static/profile_pics',picture_fn)
    
    output_size = (125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form= UpdateAccountForm()
    delete_pic= current_user.image_file
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
            if delete_pic != 'default.jpg':
                os.remove(os.path.join(app.root_path,'static/profile_pics',delete_pic))

            db.session.commit()
            flash('Your Account has been Updated!','success')
            return redirect(url_for('account'))
        
    image_file= url_for('static', filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html',title="Account", image_file=image_file, form=form)


@app.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form, legend='New Post')

@app.route('/post/<int:post_id>', methods=['GET','POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    page=request.args.get('page',1,type=int)
    comments = Comment.query.filter_by(post=post).order_by(Comment.date_posted.desc()).paginate(page=page,per_page=5)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, author=current_user, post = post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!','success')
        return redirect(url_for('post',post_id=post_id))
    return render_template('post.html', title=post.title,post=post,form=form, comments=comments)

@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
    post= Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title= form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method== 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',title='Update Post',form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
    post= Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post=post).all()
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    for i in comments:
        db.session.delete(i)
    db.session.commit()
    flash('Your post has been deleted!','success')
    return redirect(url_for('home'))



@app.route('/post<int:post_id>/comment<int:cmt_id>/edit',methods=['GET','POST'])
@login_required
def edit_comment(cmt_id,post_id):
    cmt= Comment.query.get_or_404(cmt_id)
    if cmt.author != current_user:
        abort(403)
    form=CommentForm()
    if form.validate_on_submit():
        cmt.content = form.content.data
        db.session.commit()
        flash('Your comment has been updated!','success')
        return redirect(url_for('post',post_id=post_id))
    elif request.method== 'GET':
        form.content.data = cmt.content
    return render_template('edit_cmt.html',title='Update Comment',form=form, legend='Edit Comment')

@app.route('/post<int:post_id>/comment<int:cmt_id>/delete',methods=['POST'])
@login_required
def delete_cmt(cmt_id,post_id):
    cmt= Comment.query.get_or_404(cmt_id)
    if cmt.author != current_user:
        abort(403)
    db.session.delete(cmt)
    db.session.commit()
    flash('Your comment has been deleted!','success')
    return redirect(url_for('post',post_id=post_id))


@app.route("/<vregno>/posts")
@login_required
def userPosts(vregno):
    page=request.args.get('page',1,type=int)
    user= Users.query.filter_by(vregno=vregno).first_or_404()
    posts=Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=7)
    return render_template('userPosts.html',posts=posts,user=user,title= vregno+" Posts")







@app.route('/<user>/contribute')
@login_required
def contribute(user):
    on=Courses.query.filter_by(batch=current_user.batch)
    return render_template('contribute.html', title="Contribute",contributeOn=on)







def save_file(facultypic,course):
    random_hex= secrets.token_hex(8)
    _ , f_ext = os.path.splitext(facultypic.filename)
    pic_fn = current_user.vregno + course+ random_hex + f_ext
    pic_path= os.path.join(app.root_path,'static/Resources',pic_fn)
    
    facultypic.save(pic_path)
    
    return pic_path, pic_fn

@app.route('/<user>/contribute/<sub>/upload',methods=['GET','POST'])
@login_required
def upload_resources(user,sub):
    form=ContributeResourcesForm()
    if form.validate_on_submit():
        if form.files.data:
            pic_path,file_name=save_file(form.files.data,sub)
            resource = Resources(batch=current_user.batch, course=sub,topic=form.topic.data, resource_file_path=pic_path,resource_file_name=file_name,author=current_user)
            db.session.add(resource)
            db.session.commit()
            flash('Your file has been uploaded!','success')
        else:
            flash('Please select a file!','danger')
        return redirect(url_for('upload_resources',user=current_user.vregno,sub=sub))

    page=request.args.get('page',1,type=int)
    available_files= Resources.query.filter(Resources.batch.contains(current_user.batch),Resources.resource_file_name.contains(current_user.vregno+sub)).order_by(Resources.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('uploadResources.html', title="Upload",form=form,available_files=available_files,course=sub,user=user)






@app.route('/resources')
@login_required
def resources():
    available_resources= Resources.query.filter(Resources.batch.contains(current_user.batch))
    c={}
    for available in available_resources:
        if available.course not in c:
            facultydata=Courses.query.filter_by(batch=current_user.batch,course=available.course).first()
            c[available.course]=(facultydata.faculty_name,facultydata.faculty_pic)      
    return render_template('resources.html', title="Resources",available_resources=c)


@app.route('/contributions/<user>')
@login_required
def user_resources(user):
    available_resources= Resources.query.filter(Resources.batch.contains(current_user.batch),Resources.user_id.contains(current_user.id))
    c={}
    for available in available_resources:
        if available.course not in c:
            facultydata=Courses.query.filter_by(batch=current_user.batch,course=available.course).first()
            c[available.course]=(facultydata.faculty_name,facultydata.faculty_pic)
    return render_template('resources.html', title="Resources",available_resources=c,user=user) 



@app.route('/resources/<sub>')
@login_required
def resources_contributers(sub):
    page=request.args.get('page',1,type=int)
    contributers= Resources.query.filter(Resources.batch.contains(current_user.batch),Resources.resource_file_name.contains(sub)).paginate(page=page,per_page=10)
    unique_contributers=[]
    for unique in contributers.items:
        if unique.author not in unique_contributers:
            unique_contributers.append(unique.author)
    return render_template('resourceContributers.html',contributers=unique_contributers,course=sub,cpage=contributers)


@app.route('/contributions/<sub>/<contributer>')
@login_required
def user_contributer_files(sub,contributer):
    page=request.args.get('page',1,type=int)
    cfiles= Resources.query.filter(Resources.batch.contains(current_user.batch),Resources.resource_file_name.contains(contributer+sub)).order_by(Resources.date_posted.desc()).paginate(page=page,per_page=7)
    from_account='yes'
    return render_template('contributerFiles.html',cfiles=cfiles,contributer=contributer,from_account=from_account,sub=sub,title="Downloads")

@app.route('/resources/<sub>/<contributer>')
@login_required
def contributer_files(sub,contributer):
    page=request.args.get('page',1,type=int)
    cfiles= Resources.query.filter(Resources.batch.contains(current_user.batch),Resources.resource_file_name.contains(contributer+sub)).order_by(Resources.date_posted.desc()).paginate(page=page,per_page=7)
    return render_template('contributerFiles.html',cfiles=cfiles,contributer=contributer,sub=sub,title="Downloads")

@app.route('/downloads/<file>')
@login_required
def download(file):
    dfile=Resources.query.filter_by(batch=current_user.batch, resource_file_name=file).first_or_404()
    return send_file(dfile.resource_file_path, attachment_filename=dfile.resource_file_name)


@app.route('/<user>/resource/<sub>/<rID>/edit',methods=['GET','POST'])
@login_required
def edit_resource(user,sub,rID):
    resourcez= Resources.query.get_or_404(rID)
    delete_file= resourcez.resource_file_path
    if resourcez.author != current_user or user!= current_user.vregno:
        abort(403)
    form=ContributeResourcesForm()
    if form.validate_on_submit():
        resourcez.topic=form.topic.data
        if form.files.data:
            pic_path,file_name=save_file(form.files.data,sub)
            resourcez.resource_file_path=pic_path
            resourcez.resource_file_name=file_name
            os.remove(delete_file)

        db.session.commit()
        flash('Your file has been updated!','success')
        return redirect(url_for('user_contributer_files',contributer=current_user.vregno,sub=sub))

    elif request.method== 'GET':
        form.topic.data= resourcez.topic
    return render_template('editResource.html', title="Edit",form=form,resourcez=resourcez)



@app.route('/<user>/resource/<sub>/<rID>/delete',methods=['POST'])
@login_required
def delete_resource(user,sub,rID):
    resourcez= Resources.query.get_or_404(rID)
    delete_file= resourcez.resource_file_path
    if resourcez.author != current_user or user!= current_user.vregno:
        abort(403)
    os.remove(delete_file)
    db.session.delete(resourcez)
    db.session.commit()
    flash('Your file has been deleted!','success')
    return redirect(url_for('user_contributer_files',contributer=current_user.vregno,sub=sub))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@sharesaga.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email.
'''
    mail.send(msg)



@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password. Please check your email!', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('The token is either expired or invalid!', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
