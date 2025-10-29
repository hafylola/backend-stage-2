from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from django.http import HttpResponse
from django.http import FileResponse
import requests
import random
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Country
from .serializers import CountrySerializer


@api_view(['GET'])
def get_countries(request):
    """
    GET /countries - Get all countries with filtering and sorting
    Supports: ?region=Africa | ?currency=NGN | ?sort=gdp_desc
    """
    countries = Country.objects.all()

    # Filter by region (e.g., ?region=Africa)
    region = request.GET.get('region')
    if region:
        countries = countries.filter(region__icontains=region)

    # Filter by currency (e.g., ?currency=NGN)
    currency = request.GET.get('currency')
    if currency:
        countries = countries.filter(currency_code__iexact=currency)

    # Sorting (e.g., ?sort=gdp_desc or ?sort=gdp_asc)
    sort = request.GET.get('sort')
    if sort == 'gdp_desc':
        countries = countries.order_by('-estimated_gdp')
    elif sort == 'gdp_asc':
        countries = countries.order_by('estimated_gdp')
    elif sort == 'population_desc':
        countries = countries.order_by('-population')
    elif sort == 'population_asc':
        countries = countries.order_by('population')
    elif sort == 'name_asc':
        countries = countries.order_by('name')
    elif sort == 'name_desc':
        countries = countries.order_by('-name')

    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data)

@api_view(['GET']) 
def get_country_by_name(request, name):
    """
    GET /countries/:name - Get one country by name
    """
    try:
        country = Country.objects.get(name__iexact=name)  # Case-insensitive search
        serializer = CountrySerializer(country)
        return Response(serializer.data)
    except Country.DoesNotExist:
        return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def status_view(request):
    """
    GET /status - Show total countries and last refresh timestamp
    """
    total_countries = Country.objects.count()

    # Get the most recent refresh timestamp
    latest_country = Country.objects.order_by('-last_refreshed_at').first()
    last_refreshed = latest_country.last_refreshed_at if latest_country else None

    return Response({
        "total_countries": total_countries,
        "last_refreshed_at": last_refreshed
    })

def generate_summary_image():
    """
    Generate summary image with total countries, top 5 GDP countries, and timestamp
    """
    try:
        # Get data for the image
        total_countries = Country.objects.count()
        top_countries = Country.objects.exclude(estimated_gdp__isnull=True).order_by('-estimated_gdp')[:5]
        latest_country = Country.objects.order_by('-last_refreshed_at').first()
        timestamp = latest_country.last_refreshed_at if latest_country else "Never"

        # Create image
        img_width, img_height = 600, 400
        image = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(image)

        # Try to use a font (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            font = ImageFont.load_default()

        # Draw title
        draw.text((50, 30), "Countries Summary", fill='black', font=title_font)

        # Draw total countries
        draw.text((50, 80), f"Total Countries: {total_countries}", fill='black', font=font)

        # Draw top 5 GDP countries
        draw.text((50, 120), "Top 5 Countries by GDP:", fill='black', font=font)
        y_position = 150
        for i, country in enumerate(top_countries, 1):
            gdp_formatted = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
            draw.text((70, y_position), f"{i}. {country.name}: ${gdp_formatted}", fill='black', font=font)
            y_position += 30

        # Draw timestamp
        draw.text((50, 300), f"Last Updated: {timestamp}", fill='gray', font=font)

        # Save to MEDIA_ROOT instead of custom cache folder
        image_path = os.path.join(settings.MEDIA_ROOT, 'summary.png')

        # Ensure directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Save image
        image.save(image_path)

        return True
    except Exception as e:
        print(f"Error generating image: {e}")
        return False

@api_view(['POST'])
def refresh_countries(request):
    """
    POST /countries/refresh - Fetch data from external APIs and update database
    """
    try:
        # Step 1: Fetch countries data from RestCountries API
        countries_response = requests.get(
            "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
        )

        if countries_response.status_code != 200:
            return Response(
                {"error": "External data source unavailable", "details": "Could not fetch data from RestCountries API"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        countries_data = countries_response.json()

        #  Fetch exchange rates
        exchange_response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")

        if exchange_response.status_code != 200:
            return Response(
                {"error": "External data source unavailable", "details": "Could not fetch data from Exchange Rates API"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        exchange_rates = exchange_response.json()["rates"]

        # Step 3: Process each country
        updated_count = 0
        created_count = 0

        for country_data in countries_data:
            # Extract currency code (take first currency if available)
            currency_code = None
            if country_data.get('currencies') and len(country_data['currencies']) > 0:
                currency_code = country_data['currencies'][0].get('code')

            # Get exchange rate for this currency
            exchange_rate = None
            estimated_gdp = None

            if currency_code and currency_code in exchange_rates:
                exchange_rate = exchange_rates[currency_code]
                # Calculate estimated GDP: population × random(1000–2000) ÷ exchange_rate
                random_multiplier = random.randint(1000, 2000)
                estimated_gdp = (country_data['population'] * random_multiplier) / exchange_rate

            # Create or update country record
            country_obj, created = Country.objects.update_or_create(
                name=country_data['name'],
                defaults={
                    'capital': country_data.get('capital'),
                    'region': country_data.get('region'),
                    'population': country_data.get('population', 0),
                    'currency_code': currency_code,
                    'exchange_rate': exchange_rate,
                    'estimated_gdp': estimated_gdp,
                    'flag_url': country_data.get('flag'),
                    'last_refreshed_at': timezone.now()
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            "status": "success",
            "message": f"Refreshed {len(countries_data)} countries",
            "created": created_count,
            "updated": updated_count
        })

    except requests.RequestException as e:
        return Response(
            {"error": "External data source unavailable", "details": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['DELETE'])
def delete_country(request, name):
    """
    DELETE /countries/:name - Delete a country by name
    """
    try:
        country = Country.objects.get(name__iexact=name)
        country.delete()
        return Response({"message": f"Country {name} deleted successfully"})
    except Country.DoesNotExist:
        return Response({"error": "Country not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def countries_image(request):
    """
    GET /countries/image - Serve summary image
    """
    # Try multiple possible image locations
    possible_paths = [
        os.path.join(settings.MEDIA_ROOT, 'summary.png'),
        os.path.join(settings.BASE_DIR, 'cache', 'summary.png'),
        os.path.join(settings.BASE_DIR, 'media', 'summary.png'),
    ]

    image_path = None
    for path in possible_paths:
        if os.path.exists(path):
            image_path = path
            break

    if not image_path:
        # Return EXACT error message required by the task
        return Response({"error": "Summary image not found"}, status=404)

    # Serve the image file directly
    try:
        with open(image_path, 'rb') as image_file:
            return HttpResponse(image_file.read(), content_type='image/png')
    except Exception as e:
        return Response({"error": "Summary image not found"}, status=404)




