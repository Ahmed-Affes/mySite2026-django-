# Magasin App Structure

This Django app has been organized for better maintainability and scalability.

## Directory Structure

```
magasin/
├── __init__.py
├── admin.py                    # Django admin configuration
├── apps.py                     # Django app configuration
├── decorators/                 # Custom decorators
│   ├── __init__.py
│   ├── auth.py                # Authentication decorators
│   └── views_roles.py         # Role-based access decorators
├── forms.py                    # Django forms
├── management/                 # Django management commands
├── migrations/                 # Database migrations
├── models.py                   # Database models
├── static/                     # Static files for this app
├── templates/                  # HTML templates
├── tests.py                    # Test cases
├── urls.py                     # URL patterns
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── context_processors.py  # Template context processors
└── views.py                    # Main view functions and classes
```

## Key Features

- **Organized Structure**: Separated concerns into logical directories
- **Custom Decorators**: Authentication and role-based access control
- **Utility Functions**: Reusable helper functions
- **Clean Imports**: Optimized import statements

## Components

### Decorators
- `auth.py`: Contains the custom `login_required` decorator
- `views_roles.py`: Role-based decorators (`employe_required`, `admin_required`)

### Utils
- `context_processors.py`: Template context processors for global template variables

## Usage

The app maintains full functionality while providing a cleaner, more maintainable structure for future development.
