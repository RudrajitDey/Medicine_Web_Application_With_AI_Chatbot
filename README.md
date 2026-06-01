# Medicine Web Application With AI Chatbot

A Django-based medicine e-commerce platform with integrated AI medical chatbot support.

## Overview

This project provides a full-stack online medicine marketplace that includes:
- product browsing and management
- user authentication and account management
- shopping cart and checkout flow
- order placement and email confirmation
- medical AI chatbot for text and image-based queries
- admin dashboard for store and inventory control

## Key Features

- User registration, login, and profile handling
- Multiple medicine product types with images and stock management
- Add to cart, update cart, and checkout
- Order creation, payment status handling, and confirmation emails
- AI-powered medical chatbot with:
  - text-based medical advice
  - medical image analysis support
  - session history stored per user
- Custom error pages for connection and missing routes

## Technology Stack

- Python
- Django 5.2.x
- SQLite (default development database)
- Google Gemini / `google-generative-ai` for AI chatbot
- Django templates, static files, and media uploads
- `python-dotenv` for environment configuration
- `markdown` for chatbot response rendering

## Setup Instructions

1. Clone the repository

```bash
git clone <repository-url>
cd "Medicine Web Store With AI Assistant\Medicine_Store"
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies

```bash
pip install Django==5.2.8 python-dotenv google-generative-ai markdown Pillow
```

4. Create a `.env` file in the project root and add your environment variables

```env
GOOGLE_API_KEY=your_google_api_key_here
```

5. Apply database migrations

```bash
python manage.py migrate
```

6. Create a superuser for the Django admin

```bash
python manage.py createsuperuser
```

7. Run the development server

```bash
python manage.py runserver
```

8. Open your browser at

```text
http://127.0.0.1:8000/
```

## Project Structure

- `Home/` — product listing, categories, and store homepage
- `Chatbot/` — AI medical chatbot UI and API endpoints
- `accounts/` — authentication, user account management
- `cart/` — shopping cart and cart context handling
- `orders/` — order placement, payment processing, email notifications
- `admin_panel/` — admin dashboard and seller product management
- `Medicine_Store/` — project settings, URL config, error handlers
- `templates/` — HTML templates for all pages
- `static/` — application CSS, JS, and images
- `media/` — uploaded product and chat images

## Important Notes

- This project uses Gmail SMTP settings by default in `Medicine_Store/settings.py`. Replace the hard-coded email credentials with secure environment variables before deploying.
- The app currently stores data in `db.sqlite3` and is configured for development use.
- The chatbot requires a valid `GOOGLE_API_KEY` and the `google-generative-ai` package.

## Recommended Improvements

- Move email and secret key values into `.env` securely
- Add a `requirements.txt` file for dependency tracking
- Implement production-ready payment gateway integration
- Harden deployment settings for security and allowed hosts

## License

This repository does not include a license file. Add one if you intend to share or publish the code.
