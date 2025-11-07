import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ojoto-union-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ojoto_union.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)  # Added admin field

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_coordinator(self):
        return self.role == 'coordinator'


# Announcement Model
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_urgent = db.Column(db.Boolean, default=False)


# Updated Question Model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)

    # Relationship with answers
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')


# Updated Answer Model
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_accepted = db.Column(db.Boolean, default=False)


# Discussion Model (for community forum)
class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    topic = db.Column(db.String(50), default='general')
    author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with replies
    replies = db.relationship('DiscussionReply', backref='discussion', lazy=True, cascade='all, delete-orphan')


# DiscussionReply Model
class DiscussionReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Community Comment Model
class CommunityComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'), nullable=False)


# Community Post Model
class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_pinned = db.Column(db.Boolean, default=False)

    # Relationship with comments
    comments = db.relationship('CommunityComment', backref='post', lazy=True, cascade='all, delete-orphan')


# Member Directory Model
class MemberProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with User
    user = db.relationship('User', backref=db.backref('profile', uselist=False))


# Volunteer Opportunity Model
class VolunteerOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    skills_needed = db.Column(db.String(300))
    time_commitment = db.Column(db.String(100))
    is_urgent = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with volunteer applications
    applications = db.relationship('VolunteerApplication', backref='opportunity', lazy=True,
                                   cascade='all, delete-orphan')


# Volunteer Application Model
class VolunteerApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('volunteer_opportunity.id'), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    applicant_phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    skills = db.Column(db.String(300))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================================
# UPDATED: Initialize Database Function
# ============================================================================
def initialize_database():
    """Initialize database tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")

            # Check if we need to create an admin user
            if User.query.count() == 0:
                print("ℹ️  No users found, database is fresh")
        except Exception as e:
            print(f"❌ Database error: {e}")


# ============================================================================
# UPDATED: Initialize Database Function - Modern Approach
# ============================================================================
def initialize_database():
    """Initialize database tables"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")

            # Check if we need to create an admin user
            if User.query.count() == 0:
                print("ℹ️  No users found, database is fresh")
        except Exception as e:
            print(f"❌ Database error: {e}")


# Initialize database immediately when app starts
initialize_database()


# ============================================================================
# ADDED: Debug routes for database status
# ============================================================================
@app.route('/reset-db')
def reset_db():
    """Temporary route to reset database - remove in production"""
    try:
        db.drop_all()
        db.create_all()
        return """
        <h1>Database Reset Successfully!</h1>
        <p>All tables have been recreated with the latest schema.</p>
        <p><a href='/register'>Try registering now</a></p>
        <p><a href='/debug/db'>Check database status</a></p>
        """
    except Exception as e:
        return f"<h1>Reset failed: {e}</h1>"

@app.route('/debug/db')
def debug_db():
    """Check database status and tables"""
    try:
        # Check if tables exist and have correct columns
        users_count = User.query.count()

        result = f"""
        <h1>Database Status</h1>
        <p><strong>Total Users:</strong> {users_count}</p>
        <p><strong>Database File:</strong> ojoto_union.db</p>
        <p><strong>Tables Created:</strong> ✅</p>
        <p><strong>Schema Updated:</strong> ✅ (includes is_admin column)</p>
        <hr>
        <p><a href='/register'>Register New User</a></p>
        <p><a href='/debug/users'>View All Users</a></p>
        """
        return result
    except Exception as e:
        return f"<h1>Database Error</h1><p>{e}</p>"


@app.route('/debug/users')
def debug_users():
    """Display all users in the database"""
    try:
        users = User.query.all()
        result = f"<h1>Total Users: {len(users)}</h1>"
        for user in users:
            result += f"""
            <div style='border: 1px solid #ccc; padding: 10px; margin: 10px;'>
                <p><strong>ID:</strong> {user.id}</p>
                <p><strong>Username:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Role:</strong> {user.role}</p>
                <p><strong>Is Admin:</strong> {user.is_admin}</p>
            </div>
            """
        return result + "<p><a href='/register'>Register Another User</a></p>"
    except Exception as e:
        return f"<h1>Error: {e}</h1>"


# ============================================================================
# UPDATED: Routes with better error handling
# ============================================================================
@app.route('/')
def index():
    try:
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
        print(f"Found {len(announcements)} announcements")
        return render_template('index.html', announcements=announcements)
    except Exception as e:
        print(f"ERROR: {e}")
        return render_template('index.html', announcements=[])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form.get('role', 'student')

            print(f"🔄 Attempting to register user: {username}, {email}")

            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists!', 'error')
                return redirect(url_for('register'))

            if User.query.filter_by(email=email).first():
                flash('Email already exists!', 'error')
                return redirect(url_for('register'))

            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            print(f"✅ User {username} registered successfully!")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            print(f"❌ REGISTRATION ERROR: {str(e)}")
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['email'] = user.email
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/post_announcement', methods=['GET', 'POST'])
def post_announcement():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_urgent = 'is_urgent' in request.form

        new_announcement = Announcement(
            title=title,
            content=content,
            author=session['username'],
            is_urgent=is_urgent
        )

        db.session.add(new_announcement)
        db.session.commit()

        flash('Announcement posted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('post_announcement.html')


# Q&A Forum Routes
@app.route('/questions')
def questions():
    if 'user_id' not in session:
        flash('Please login to access the Q&A Forum', 'warning')
        return redirect(url_for('login'))

    try:
        questions = Question.query.order_by(Question.created_at.desc()).all()
        return render_template('questions.html', questions=questions)
    except Exception as e:
        print(f"Error loading questions: {e}")
        return render_template('questions.html', questions=[])


@app.route('/ask_question', methods=['GET', 'POST'])
def ask_question():
    if 'user_id' not in session:
        flash('Please login to ask a question', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'general')
        is_urgent = 'is_urgent' in request.form

        new_question = Question(
            title=title,
            content=content,
            category=category,
            author=session['username'],
            user_id=session['user_id'],
            is_urgent=is_urgent
        )

        db.session.add(new_question)
        db.session.commit()
        flash('Question posted successfully!', 'success')
        return redirect(url_for('questions'))

    return render_template('ask_question.html')


@app.route('/answer_question/<int:question_id>', methods=['POST'])
def answer_question(question_id):
    if 'user_id' not in session:
        flash('Please login to answer questions', 'error')
        return redirect(url_for('login'))

    content = request.form['content']

    new_answer = Answer(
        content=content,
        author=session['username'],
        user_id=session['user_id'],
        question_id=question_id
    )

    db.session.add(new_answer)
    db.session.commit()
    flash('Answer posted successfully!', 'success')
    return redirect(url_for('questions'))


# Q&A Forum Detail View
@app.route('/question/<int:question_id>')
def question_detail(question_id):
    if 'user_id' not in session:
        flash('Please login to view questions', 'warning')
        return redirect(url_for('login'))

    question = Question.query.get_or_404(question_id)
    return render_template('question_detail.html', question=question)


# Post Answer Route
@app.route('/answer/<int:question_id>', methods=['POST'])
def post_answer(question_id):
    if 'user_id' not in session:
        flash('Please login to post an answer', 'warning')
        return redirect(url_for('login'))

    question = Question.query.get_or_404(question_id)
    content = request.form['content']

    new_answer = Answer(
        content=content,
        author=session['username'],
        user_id=session['user_id'],
        question_id=question_id
    )

    db.session.add(new_answer)
    db.session.commit()
    flash('Your answer has been posted!', 'success')
    return redirect(url_for('question_detail', question_id=question_id))


# Mark Answer as Accepted
@app.route('/accept-answer/<int:answer_id>')
def accept_answer(answer_id):
    if 'user_id' not in session:
        flash('Please login to perform this action', 'warning')
        return redirect(url_for('login'))

    answer = Answer.query.get_or_404(answer_id)

    # Check if user owns the question
    if answer.question.user_id != session['user_id']:
        flash('You can only accept answers for your own questions', 'error')
        return redirect(url_for('question_detail', question_id=answer.question_id))

    # Mark as resolved
    answer.question.is_resolved = True
    answer.is_accepted = True
    db.session.commit()

    flash('Answer accepted! Question marked as resolved.', 'success')
    return redirect(url_for('question_detail', question_id=answer.question_id))


# Community Forum Routes
@app.route('/community')
def community():
    try:
        posts = CommunityPost.query.order_by(CommunityPost.is_pinned.desc(), CommunityPost.created_at.desc()).all()
        return render_template('community.html', posts=posts)
    except Exception as e:
        print(f"Error loading community posts: {e}")
        return render_template('community.html', posts=[])


# Alternative Community Forum (Discussion-based)
@app.route('/community-forum')
def community_forum():
    if 'user_id' not in session:
        flash('Please login to access the Community Forum', 'warning')
        return redirect(url_for('login'))

    discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()
    return render_template('community_forum.html', discussions=discussions)


@app.route('/create-discussion', methods=['GET', 'POST'])
def create_discussion():
    if 'user_id' not in session:
        flash('Please login to create a discussion', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        topic = request.form.get('topic', 'general')

        new_discussion = Discussion(
            title=title,
            content=content,
            topic=topic,
            author=session['username'],
            user_id=session['user_id']
        )

        db.session.add(new_discussion)
        db.session.commit()
        flash('Discussion started successfully!', 'success')
        return redirect(url_for('community_forum'))

    return render_template('create_discussion.html')


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash('Please login to create a post', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'general')

        new_post = CommunityPost(
            title=title,
            content=content,
            author=session['username'],
            category=category
        )

        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('community'))

    return render_template('create_post.html')


@app.route('/comment_post/<int:post_id>', methods=['POST'])
def comment_post(post_id):
    if 'user_id' not in session:
        flash('Please login to comment', 'error')
        return redirect(url_for('login'))

    content = request.form['content']

    new_comment = CommunityComment(
        content=content,
        author=session['username'],
        post_id=post_id
    )

    db.session.add(new_comment)
    db.session.commit()
    flash('Comment posted successfully!', 'success')
    return redirect(url_for('community'))


@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        flash('Please login to delete posts', 'error')
        return redirect(url_for('login'))

    post = CommunityPost.query.get_or_404(post_id)

    # Only allow author or admin to delete
    if post.author == session['username'] or session.get('role') == 'admin':
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
    else:
        flash('You can only delete your own posts', 'error')

    return redirect(url_for('community'))


@app.route('/debug_announcements')
def debug_announcements():
    try:
        announcements = Announcement.query.all()
        result = f"Total announcements: {len(announcements)}<br><br>"
        for ann in announcements:
            result += f"Title: {ann.title}<br>Content: {ann.content}<br>Author: {ann.author}<br><br>"
        return result
    except Exception as e:
        return f"Error: {e}"


# Member Directory Routes
@app.route('/members')
def members():
    try:
        # Get all public member profiles with user info
        members = MemberProfile.query.filter_by(is_public=True).all()
        return render_template('members.html', members=members)
    except Exception as e:
        print(f"Error loading members: {e}")
        return render_template('members.html', members=[])


@app.route('/member/<int:member_id>')
def member_detail(member_id):
    try:
        member = MemberProfile.query.get_or_404(member_id)
        if not member.is_public:
            flash('This member profile is not public', 'error')
            return redirect(url_for('members'))
        return render_template('member_detail.html', member=member)
    except Exception as e:
        flash('Error loading member profile', 'error')
        return redirect(url_for('members'))


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Please login to edit your profile', 'error')
        return redirect(url_for('login'))

    # Get or create profile for current user
    profile = MemberProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile:
        profile = MemberProfile(
            user_id=session['user_id'],
            full_name=session['username'],
            profession="Member",
            bio="",
            is_public=True
        )
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.full_name = request.form['full_name']
        profile.phone = request.form['phone']
        profile.location = request.form['location']
        profile.profession = request.form['profession']
        profile.bio = request.form['bio']
        profile.is_public = 'is_public' in request.form
        profile.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('member_detail', member_id=profile.id))

    return render_template('edit_profile.html', profile=profile)


@app.route('/search_members')
def search_members():
    query = request.args.get('q', '')
    if query:
        members = MemberProfile.query.filter(
            MemberProfile.is_public == True,
            (MemberProfile.full_name.ilike(f'%{query}%')) |
            (MemberProfile.profession.ilike(f'%{query}%')) |
            (MemberProfile.location.ilike(f'%{query}%'))
        ).all()
    else:
        members = MemberProfile.query.filter_by(is_public=True).all()

    return render_template('members.html', members=members, search_query=query)


# Gallery Route
@app.route('/gallery')
def gallery():
    gallery_images = [
        {
            'filename': 'Image1.jpg',
            'title': 'Community Gathering',
            'description': 'Our recent community event showcasing unity and collaboration.'
        },
        {
            'filename': 'Image2.jpg',
            'title': 'Annual Meeting',
            'description': 'Members gathered for our annual general meeting and planning session.'
        },
        {
            'filename': 'Image3.jpg',
            'title': 'Cultural Celebration',
            'description': 'Celebrating our rich cultural heritage and traditions.'
        },
        {
            'filename': 'Image4.jpg',
            'title': 'Youth Empowerment',
            'description': 'Empowering the next generation through mentorship programs.'
        },
        {
            'filename': 'Image5.jpg',
            'title': 'Community Service',
            'description': 'Giving back to our community through volunteer initiatives.'
        },
        {
            'filename': 'Image6.jpg',
            'title': 'Networking Event',
            'description': 'Building connections and professional relationships.'
        },
        {
            'filename': 'Image7.jpg',
            'title': 'Family Day',
            'description': 'Bringing families together for fun and bonding activities.'
        }
    ]
    return render_template('gallery.html', gallery_images=gallery_images)


# Volunteer Opportunities Routes
@app.route('/volunteer')
def volunteer_opportunities():
    try:
        opportunities = VolunteerOpportunity.query.filter_by(is_active=True).order_by(
            VolunteerOpportunity.is_urgent.desc(),
            VolunteerOpportunity.created_at.desc()
        ).all()
        return render_template('volunteer.html', opportunities=opportunities)
    except Exception as e:
        print(f"Error loading volunteer opportunities: {e}")
        return render_template('volunteer.html', opportunities=[])


@app.route('/volunteer/<int:opportunity_id>')
def volunteer_detail(opportunity_id):
    try:
        opportunity = VolunteerOpportunity.query.get_or_404(opportunity_id)
        if not opportunity.is_active:
            flash('This volunteer opportunity is no longer available', 'error')
            return redirect(url_for('volunteer_opportunities'))
        return render_template('volunteer_detail.html', opportunity=opportunity)
    except Exception as e:
        flash('Error loading volunteer opportunity', 'error')
        return redirect(url_for('volunteer_opportunities'))


@app.route('/post_opportunity', methods=['GET', 'POST'])
def post_opportunity():
    if 'user_id' not in session:
        flash('Please login to post volunteer opportunities', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        organization = request.form['organization']
        location = request.form['location']
        contact_email = request.form['contact_email']
        contact_phone = request.form['contact_phone']
        skills_needed = request.form['skills_needed']
        time_commitment = request.form['time_commitment']
        is_urgent = 'is_urgent' in request.form

        new_opportunity = VolunteerOpportunity(
            title=title,
            description=description,
            organization=organization,
            location=location,
            contact_email=contact_email,
            contact_phone=contact_phone,
            skills_needed=skills_needed,
            time_commitment=time_commitment,
            is_urgent=is_urgent,
            created_by=session['username']
        )

        db.session.add(new_opportunity)
        db.session.commit()
        flash('Volunteer opportunity posted successfully!', 'success')
        return redirect(url_for('volunteer_opportunities'))

    return render_template('post_opportunity.html')


@app.route('/apply_volunteer/<int:opportunity_id>', methods=['GET', 'POST'])
def apply_volunteer(opportunity_id):
    opportunity = VolunteerOpportunity.query.get_or_404(opportunity_id)

    if not opportunity.is_active:
        flash('This volunteer opportunity is no longer available', 'error')
        return redirect(url_for('volunteer_opportunities'))

    if request.method == 'POST':
        applicant_name = request.form['applicant_name']
        applicant_email = request.form['applicant_email']
        applicant_phone = request.form['applicant_phone']
        message = request.form['message']
        skills = request.form['skills']

        # Check if user already applied
        existing_application = VolunteerApplication.query.filter_by(
            opportunity_id=opportunity_id,
            applicant_email=applicant_email
        ).first()

        if existing_application:
            flash('You have already applied for this opportunity', 'error')
            return redirect(url_for('volunteer_detail', opportunity_id=opportunity_id))

        new_application = VolunteerApplication(
            opportunity_id=opportunity_id,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            applicant_phone=applicant_phone,
            message=message,
            skills=skills
        )

        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('volunteer_detail', opportunity_id=opportunity_id))

    return render_template('apply_volunteer.html', opportunity=opportunity)


@app.route('/my_applications')
def my_applications():
    if 'user_id' not in session:
        flash('Please login to view your applications', 'error')
        return redirect(url_for('login'))

    try:
        applications = VolunteerApplication.query.filter_by(
            applicant_email=session.get('email', '')
        ).order_by(VolunteerApplication.applied_at.desc()).all()

        return render_template('my_applications.html', applications=applications)
    except Exception as e:
        print(f"Error loading applications: {e}")
        return render_template('my_applications.html', applications=[])


# Admin Routes
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    # Get real stats from database
    stats = {
        'total_users': User.query.count(),
        'volunteer_opportunities': VolunteerOpportunity.query.filter_by(is_active=True).count(),
        'pending_approvals': VolunteerApplication.query.filter_by(status='pending').count(),
        'recent_announcements': Announcement.query.filter(
            Announcement.created_at >= datetime.utcnow().replace(day=1)
        ).count()
    }

    # Get recent activity (last 5 announcements)
    recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    recent_activity = [
        {
            'username': ann.author,
            'action': f'Posted: {ann.title}',
            'timestamp': ann.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for ann in recent_announcements
    ]

    return render_template('admin/dashboard.html', stats=stats, recent_activity=recent_activity)


@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/announcements')
def admin_announcements():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()

    # Add created_this_month flag for statistics
    current_month = datetime.utcnow().replace(day=1)
    for ann in announcements:
        ann.created_this_month = ann.created_at >= current_month

    return render_template('admin/announcements.html', announcements=announcements)


@app.route('/admin/volunteers')
def admin_volunteers():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    opportunities = VolunteerOpportunity.query.order_by(VolunteerOpportunity.created_at.desc()).all()
    applications = VolunteerApplication.query.order_by(VolunteerApplication.applied_at.desc()).all()

    return render_template('admin/volunteers.html', opportunities=opportunities, applications=applications)


# ============================================================================
# UPDATED: Main block with proper database initialization
# ============================================================================
if __name__ == '__main__':
    print("🚀 Website running at: http://127.0.0.1:5000")
    print("✅ Database is ready with updated schema")
    print("📝 You can now register and login")
    print("❓ Q&A Forum is now active")
    print("👥 Member Directory is ready")
    print("💬 Discussion Forums are implemented")
    print("🔧 Admin Panel is now available at /admin/dashboard")
    app.run(debug=True, host='0.0.0.0', port=5000)