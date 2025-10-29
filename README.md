# Country Currency & Exchange API

A Django REST API that fetches country data from external APIs, calculates GDP estimates, and provides currency exchange information.

## 🚀 Features

- Fetch country data from RestCountries API
- Get real-time exchange rates
- Calculate estimated GDP for each country
- Filter and sort countries by various criteria
- Generate summary images
- RESTful API with proper error handling

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/countries/refresh` | Fetch latest data from external APIs |
| GET | `/countries` | Get all countries (supports filtering) |
| GET | `/countries/{name}` | Get specific country by name |
| DELETE | `/countries/{name}/delete` | Delete country record |
| GET | `/status` | Get API status and counts |
| GET | `/countries/image` | Get generated summary image |

### Filtering & Sorting
- `?region=Africa` - Filter by region
- `?currency=USD` - Filter by currency code 
- `?sort=gdp_desc` - Sort by GDP (options: `gdp_desc`, `gdp_asc`, `population_desc`, `population_asc`)

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- MySQL (or SQLite for development)

### Setup
1. **Clone repository**
   ```bash
   git clone https://github.com/hafylola/backend-stage-2.git
   cd country-currency-api

