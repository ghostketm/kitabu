# Kitabu - Notes App

Kitabu is a comprehensive Django-based web application for managing personal notes. It features user authentication, note creation, editing, sharing, and a payment system for premium features.

## Features

- **User Authentication**: Secure registration, login, and profile management
- **Note Management**: Create, read, update, and delete notes
- **Note Sharing**: Share notes with other users
- **Payment Integration**: M-Pesa integration for premium upgrades
- **Responsive Design**: Bootstrap-based UI with Tailwind CSS
- **Admin Panel**: Django admin interface for content management
- **Static File Serving**: WhiteNoise for production static files

## Technologies Used

- **Backend**: Django 5.2.6
- **Frontend**: HTML, Tailwind CSS, Bootstrap 5
- **Database**: SQLite (local) / PostgreSQL (production)
- **Payment**: M-Pesa API
- **Deployment**: Gunicorn, WhiteNoise

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ghostketm/kitabu.git
   cd kitabu
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   MPESA_CONSUMER_KEY=your-mpesa-key
   MPESA_CONSUMER_SECRET=your-mpesa-secret
   MPESA_SHORTCODE=your-shortcode
   MPESA_PASSKEY=your-passkey
   MPESA_CALLBACK_URL=your-callback-url
   MPESA_ENVIRONMENT=sandbox
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the application.

## Usage

- Register a new account or login
- Create and manage your notes
- Share notes with other users
- Upgrade to premium for additional features
- Access admin panel at `/admin/` (superuser required)

## Deployment

This app is configured for deployment on platforms like Heroku, Render, or Railway.

### Environment Variables for Production

Set the following in your deployment platform:
- `SECRET_KEY`: A secure random string
- `DEBUG`: False
- `ALLOWED_HOSTS`: Your domain(s)
- `DATABASE_URL`: PostgreSQL connection string
- `MPESA_*`: Your M-Pesa credentials

### Free Deployment Options

- **Render.com**: Connect GitHub repo, set build/start commands
- **Railway.app**: Git-based deployment with free tier
- **Fly.io**: CLI-based deployment with free resources

## Project Structure

```
kitabu/
├── accounts/          # User authentication app
├── notes/             # Notes management app
├── payments/          # Payment integration app
├── administrator/     # Admin features app
├── kitabu_project/    # Main Django project
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User-uploaded files
├── requirements.txt   # Python dependencies
├── Procfile           # Heroku deployment
├── runtime.txt        # Python version
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.
