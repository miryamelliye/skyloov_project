from django.shortcuts import render
import concurrent.futures
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from django.http import JsonResponse
import os
import concurrent.futures
from PIL import Image
from drf_yasg import openapi
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView


class ValidateAndStoreImageView(GenericAPIView):
    parser_classes = (MultiPartParser,)
    @swagger_auto_schema(
        operation_description='Validate and store an image for a product',
        operation_id='Upload image for product',
        manual_parameters=[openapi.Parameter(
                            name="image",
                            in_=openapi.IN_FORM,
                            type=openapi.TYPE_FILE,
                            required=True,
                            description="Document"
                            )],
        responses={400: 'No image data provided',
                   200: 'Image uploaded and stored successfully.'},
    )
    def post(self, request, pk):
        # Retrieve the product instance
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        if 'image' in request.FILES:
            image = request.FILES['image']
            # Performing image validation
            try:
                img = Image.open(image)
                img.verify()

                # Here we can add additional validation checks (for example:Check image format, file size, resolution..)
            except Exception as e:
                return JsonResponse({'error': 'Invalid image: ' + str(e)}, status=400)
            # Saving the original image to the product instance
            product.image = image
            product.save()
            # Generating different sizes of the image in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Defining the desired image sizes
                sizes = [
                    (100, 100),  # Thumbnail size
                    (800, 800),  # Full-size image size
                    # We can add as many sizes as needed
                ]
                # Submitting the image processing tasks to the thread pool
                # We can replace ThreadPoolExecutor with ProcessPoolExecutor to utilize multiprocessing instead of multithreading.
                futures = [executor.submit(process_image_size, product, image, size) for size in sizes]
                # Waiting for all tasks to complete
                concurrent.futures.wait(futures)
            # Returning a success response
            return JsonResponse({'success': 'Image uploaded and stored successfully.', 'product_id': product.id})
        # Return an error response if no image is provided
        return JsonResponse({'error': 'No image data provided.'}, status=400)

def process_image_size(product, image, size):
    # Opening and resizing the image to the desired size
    img = Image.open(image)
    img = img.resize(size)
    # Saving the resized image to a file and generating a unique filename based on the size
    filename = f"{product.id}_size_{size[0]}x{size[1]}.png"
    # Defining the directory path to save the images
    save_directory = os.path.join(settings.MEDIA_ROOT, 'resized_images')
    # Creating the directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    # Saving the resized image to the file
    save_path = os.path.join(save_directory, filename)
    img.save(save_path)
    # Updating the product instance with the saved image path
    # Adjusting the field name based on your product model
    product.image_path = save_path  
    product.save()
