from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import app, Blog, db, User, ext
from flask_bcrypt import Bcrypt
import marko

@app.route('/')
def index():
    return render_template('index.html')


# Add this dynamic rule to include blog URLs in the sitemap
@ext.register_generator
def blog_sitemap():
    # Get all blogs from the database
    blogs = Blog.query.all()
    for blog in blogs:
        # Generate a URL for each blog using the blog's title
        yield 'blog_detail', {'blog_title': blog.title}

@app.route('/blogs')
def blog_list():
    blogs = Blog.query.order_by(Blog.date_posted.desc()).all()
    is_admin = session.get('is_admin', False)  # Check if admin is logged in
    return render_template('blog_list.html', blogs=blogs, is_admin=is_admin)

@app.route('/blog/<string:blog_title>')
def blog_detail(blog_title):
    blog = Blog.query.filter_by(title=blog_title).first_or_404()
    content = marko.convert(blog.content)
    return render_template('blog_detail.html', blog=blog, content=content)

# Admin login route
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            session['is_admin'] = True  # Set admin status in session
            flash('You are now logged in as admin.', 'success')
            return redirect(url_for('new_blog'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin_login.html')

# Admin logout route
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)  # Remove admin from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin_login'))

# Route to delete a blog (accessible by admin only)
@app.route('/admin/delete_blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    if not session.get('is_admin'):
        flash('You do not have permission to delete this blog.', 'danger')
        return redirect(url_for('blog_list'))
    
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog has been deleted.', 'success')
    return redirect(url_for('blog_list'))

@app.route('/admin/new_blog', methods=['GET', 'POST'])
def new_blog():
    if session.get('is_admin'):
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            new_blog = Blog(title=title, content=content)
            db.session.add(new_blog)
            db.session.commit()
            return redirect(url_for('blog_list'))
        return render_template('new_blog.html')
    return redirect(url_for("admin_login"))
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
