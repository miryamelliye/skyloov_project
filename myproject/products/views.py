import concurrent.futures
from rest_framework.decorators import api_view, permission_classes, schema
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import Product
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
import os
import concurrent.futures
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings

# from django.contrib.auth.models import User
# from django.contrib.auth.hashers import check_password
# from django.contrib.auth.hashers import make_password

from .tasks import send_welcome_email

class ProductSearchPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum number of items per page


@swagger_auto_schema(
    method='GET',
    operation_description='Search products based on various criteria',
    manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, description='Category of the product', type=openapi.TYPE_STRING),
        openapi.Parameter('brand', openapi.IN_QUERY, description='Brand of the product', type=openapi.TYPE_STRING),
        openapi.Parameter('min_price', openapi.IN_QUERY, description='Minimum price of the product', type=openapi.TYPE_NUMBER),
        openapi.Parameter('max_price', openapi.IN_QUERY, description='Maximum price of the product', type=openapi.TYPE_NUMBER),
        openapi.Parameter('min_quantity', openapi.IN_QUERY, description='Minimum quantity of the product', type=openapi.TYPE_INTEGER),
        openapi.Parameter('max_quantity', openapi.IN_QUERY, description='Maximum quantity of the product', type=openapi.TYPE_INTEGER),
        openapi.Parameter('created_at', openapi.IN_QUERY, description='Created date of the product', type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        openapi.Parameter('rating', openapi.IN_QUERY, description='Rating of the product', type=openapi.TYPE_NUMBER),
        openapi.Parameter('sort', openapi.IN_QUERY, description='Sorting order (e.g., price)', type=openapi.TYPE_STRING),
    ],
    responses={200: openapi.Response(description='Successful response', schema=ProductSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_search_view(request):
    """
    Search products based on various criteria.

    Available query parameters:
    - category (optional): Category of the product
    - brand (optional): Brand of the product
    - min_price (optional): Minimum price of the product
    - max_price (optional): Maximum price of the product
    - min_quantity (optional): Minimum quantity of the product
    - max_quantity (optional): Maximum quantity of the product
    - created_at (optional): Created date of the product
    - rating (optional): Rating of the product

    Sorting:
    - Use the 'sort' query parameter to specify the sorting order (e.g., 'sort=price' for sorting by price).

    Returns a paginated list of products matching the search criteria.
    """
    serializer = ProductSearchSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    # Retrieve search criteria from the serializer
    category = serializer.validated_data.get('category')
    brand = serializer.validated_data.get('brand')
    min_price = serializer.validated_data.get('min_price')
    max_price = serializer.validated_data.get('max_price')
    min_quantity = serializer.validated_data.get('min_quantity')
    max_quantity = serializer.validated_data.get('max_quantity')
    created_at = serializer.validated_data.get('created_at')
    rating = serializer.validated_data.get('rating')
    sort = request.query_params.get('sort')  # Retrieve the sort parameter from the request

    # Build the query based on the search criteria
    query = Product.objects.all()
    if category:
        query = query.filter(category=category)
    if brand:
        query = query.filter(brand=brand)
    if min_price:
        query = query.filter(price__gte=min_price)
    if max_price:
        query = query.filter(price__lte=max_price)
    if min_quantity:
        query = query.filter(quantity__gte=min_quantity)
    if max_quantity:
        query = query.filter(quantity__lte=max_quantity)
    if created_at:
        query = query.filter(created_at__date=created_at.date())
    if rating:
        query = query.filter(rating=rating)

    # Apply sorting to the query
    if sort:
        query = query.order_by(sort)

    # Retrieve the matching products
    products = query.all()

    # # Serialize the products and return the response
    # product_serializer = ProductSerializer(products, many=True)
    # return Response(product_serializer.data)

    # Apply pagination to the query
    paginator = ProductSearchPagination()
    paginated_results = paginator.paginate_queryset(products, request)

    # Serialize the paginated results
    product_serializer = ProductSerializer(paginated_results, many=True)

    # Return the paginated response
    return paginator.get_paginated_response(product_serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    # Retrieve the product object
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message': 'Product not found'}, status=404)

    # Create a new cart item
    cart_item = CartItem.objects.create(user=request.user, product=product, quantity=1)

    # Serialize the cart item
    serializer = CartItemSerializer(cart_item)

    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_item_id):
    # Get the cart item object
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    except CartItem.DoesNotExist:
        return Response({'message': 'Cart item not found'}, status=404)

    # Update the quantity of the cart item
    quantity = request.data.get('quantity')
    cart_item.quantity = quantity
    cart_item.save()

    # Serialize the updated cart item
    serializer = CartItemSerializer(cart_item)

    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, cart_item_id):
    # Get the cart item object
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    except CartItem.DoesNotExist:
        return Response({'message': 'Cart item not found'}, status=404)

    # Delete the cart item
    cart_item.delete()

    return Response({'message': 'Cart item removed'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    # Retrieve all cart items for the current user
    cart_items = CartItem.objects.filter(user=request.user)

    # Serialize the cart items
    serializer = CartItemSerializer(cart_items, many=True)

    return Response(serializer.data)

@api_view(['POST'])
def upload_product_image(request):
    if 'image' in request.FILES:
        image = request.FILES['image']

        # Perform any necessary processing or validation on the image

        # Create the directory if it doesn't exist
        image_directory = 'static/images/product_images/'
        os.makedirs(image_directory, exist_ok=True)

        # Save the image to the desired location
        image_path = os.path.join(image_directory, image.name)
        with open(image_path, 'wb') as file:
            for chunk in image.chunks():
                file.write(chunk)

        # Return a success response
        return JsonResponse({'success': 'Image uploaded successfully.'})

    # Return an error response if no image is provided
    return JsonResponse({'error': 'No image data provided.'}, status=400)


# the concurrent.futures.ThreadPoolExecutor() is used to create a thread pool, allowing parallel execution of the process_image function. You can replace ThreadPoolExecutor with ProcessPoolExecutor to utilize multiprocessing instead.


@csrf_exempt
@api_view(['POST'])
@swagger_auto_schema(
    operation_description='Validate and store an image for a product',
    consumes=["multipart/form-data"],  # Add this line to specify the content type
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['image'],
        properties={
            'image': openapi.Schema(
                type=openapi.TYPE_FILE,
                description='Image file to upload'
            )
        }
    ),
    responses={
        200: 'Image uploaded and stored successfully.',
        400: 'Invalid image or no image data provided.',
        404: 'Product not found.'
    }
)
def validate_and_store_image(request, pk):
    # Retrieve the product instance
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    if 'image' in request.FILES:
        image = request.FILES['image']

        # Perform image validation
        try:
            img = Image.open(image)
            img.verify()  # Verify the image data integrity

            # Add additional validation checks here
            # For example:
            # - Check image format, file size, resolution, etc.

        except Exception as e:
            return JsonResponse({'error': 'Invalid image: ' + str(e)}, status=400)

        # Save the original image to the product instance
        product.image = image
        product.save()

        # Generate different sizes of the image in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Define the desired image sizes
            sizes = [
                (100, 100),  # Thumbnail size
                (800, 800),  # Full-size image size
                # Add more sizes as needed
            ]

            # Submit the image processing tasks to the thread pool
            futures = [executor.submit(process_image_size, product, image, size) for size in sizes]

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

        # Return a success response
        return JsonResponse({'success': 'Image uploaded and stored successfully.', 'product_id': product.id})

    # Return an error response if no image is provided
    return JsonResponse({'error': 'No image data provided.'}, status=400)



def process_image_size(product, image, size):
    # Open and resize the image to the desired size
    img = Image.open(image)
    img = img.resize(size)

    # Save the resized image to a file
    # Generate a unique filename based on the size
    filename = f"{product.id}_size_{size[0]}x{size[1]}.png"

    # Define the directory path to save the images
    save_directory = os.path.join(settings.MEDIA_ROOT, 'resized_images')

    # Create the directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    # Save the resized image to the file
    save_path = os.path.join(save_directory, filename)
    img.save(save_path)

    # Update the product instance with the saved image path
    # Adjust the field name based on your product model
    product.image_path = save_path  # For example, save the image path to a separate field
    product.save()

import datetime


@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: 'User registered successfully.',
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_welcome_email.apply_async(args=(user.id,), countdown=20)  # Set countdown to 10 seconds
        # send_welcome_email.apply_async(args=(user.id,), countdown=timedelta(days=1).total_seconds())
        current_time = datetime.datetime.now()
        print("Current time:", current_time)
        return Response({'message': 'User registered successfully.'})
    return Response(serializer.errors, status=400)

@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: 'User registered successfully.',
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def login(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
    


