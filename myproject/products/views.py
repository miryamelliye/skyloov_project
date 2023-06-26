import concurrent.futures
from rest_framework.decorators import api_view, permission_classes, action
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
from .tasks import send_welcome_email
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
# Custom pagination class for product search functionality
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

    # Retrieving search criteria from the serializer
    category = serializer.validated_data.get('category')
    brand = serializer.validated_data.get('brand')
    min_price = serializer.validated_data.get('min_price')
    max_price = serializer.validated_data.get('max_price')
    min_quantity = serializer.validated_data.get('min_quantity')
    max_quantity = serializer.validated_data.get('max_quantity')
    created_at = serializer.validated_data.get('created_at')
    rating = serializer.validated_data.get('rating')

    # Retrieving the sort parameter from the request
    sort = request.query_params.get('sort')  

    # Building the query based on the search criteria
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

    # Applying sorting to the query
    if sort:
        query = query.order_by(sort)

    # Retrieveing the matching products
    products = query.all()

    # Applying pagination to the query
    paginator = ProductSearchPagination()
    paginated_results = paginator.paginate_queryset(products, request)

    # Serializing the paginated results
    product_serializer = ProductSerializer(paginated_results, many=True)

    # Returning the paginated response
    return paginator.get_paginated_response(product_serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message': 'Product not found'})

    # Checking if the cart item already exists for the product
    try:
        CartItem.objects.get(user=request.user, product=product)
        # Cart item already exists, do nothing
        return Response({'message': 'Cart item already exists'})
    except CartItem.DoesNotExist:
        # Creating a new cart item
        cart_item = CartItem.objects.create(user=request.user, product=product, quantity=1)

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)

@swagger_auto_schema(
    method='PUT',
    operation_description='Update the quantity of a cart item',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ),
    responses={
        200: 'OK',
        404: 'Cart item not found'
    }
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_item_id):
    # Getting the cart item object
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    except CartItem.DoesNotExist:
        return Response({'message': 'Cart item not found'}, status=404)
    # Updating the quantity of the cart item
    quantity = request.data.get('quantity')
    cart_item.quantity = quantity
    cart_item.save()
    # Serializing the updated cart item
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, cart_item_id):
    # Getting the cart item object
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    except CartItem.DoesNotExist:
        return Response({'message': 'Cart item not found'}, status=404)
    # Deleting the cart item
    cart_item.delete()
    return Response({'message': 'Cart item removed'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    # Retrieving all cart items for the current user
    cart_items = CartItem.objects.filter(user=request.user)
    # Serializing the cart items
    serializer = CartItemSerializer(cart_items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def upload_product_image(request):
    if 'image' in request.FILES:
        image = request.FILES['image']
        # Creating the directory if it doesn't exist
        image_directory = 'static/images/product_images/'
        os.makedirs(image_directory, exist_ok=True)
        # Saving the image to the desired location
        image_path = os.path.join(image_directory, image.name)
        with open(image_path, 'wb') as file:
            for chunk in image.chunks():
                file.write(chunk)
        # Returning a success response
        return JsonResponse({'success': 'Image uploaded successfully.'})
    # Returning an error response if no image is provided
    return JsonResponse({'error': 'No image data provided.'}, status=400)

