from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly



class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]




import uuid
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payments
from .tasks import send_payment_success_email

CHAPA_API_URL = settings.CHAPA_BASE_URL


class InitiatePaymentView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []      # Public endpoint

    def post(self, request):
        try:
            # Get data from request body
            amount = request.data.get("amount")
            email = request.data.get("email")
            first_name = request.data.get("first_name", "John")
            last_name = request.data.get("last_name", "Doe")

            # Validate input fields
            if not amount or not email:
                return Response(
                    {"status": "failed", "message": "Amount and email are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate unique transaction reference
            tx_ref = f"tx-{uuid.uuid4()}"

            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            # Prepare payload for Chapa API
            payload = {
                "amount": str(amount),
                "currency": "ETB",
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "tx_ref": tx_ref,
                "callback_url": "http://127.0.0.1:8000/api/payments/verify/",
                "return_url": "http://127.0.0.1:8000/payment-success/",
                "customization": {
                    "title": "Payment for Booking",
                    "description": "Secure payment via Chapa"
                }
            }

            # Call Chapa API
            response = requests.post(f"{CHAPA_API_URL}/initialize", json=payload, headers=headers)
            chapa_response = response.json()

            # Check Chapa response
            if chapa_response.get("status") != "success":
                return Response(
                    {"status": "failed", "message": chapa_response.get("message", "Payment initialization failed")},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save payment to database
            Payments.objects.create(
                amount=amount,
                email=email,
                booking_reference=tx_ref,
                status="Pending",
                user=None  # Anonymous for now
            )

            return Response({
                "status": "success",
                "message": "Payment initialized successfully",
                "checkout_url": chapa_response["data"]["checkout_url"],
                "tx_ref": tx_ref
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": "failed", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyPaymentView(APIView):
    authentication_classes = []  # No authentication required
    permission_classes = []      # Public endpoint

    def get(self, request):
        try:
            # Get transaction reference from query params
            tx_ref = request.query_params.get("tx_ref")
            if not tx_ref:
                return Response(
                    {"status": "failed", "message": "Transaction reference is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare headers
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            # Call Chapa API for verification
            response = requests.get(f"{CHAPA_API_URL}/verify/{tx_ref}", headers=headers)
            chapa_response = response.json()

            # Find payment in DB
            try:
                payment = Payments.objects.get(booking_reference=tx_ref)
            except Payments.DoesNotExist:
                return Response(
                    {"status": "failed", "message": "Payment not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Update payment status
            if chapa_response.get("status") == "success":
                payment.status = "Completed"
                payment.save()

                # Send confirmation email
                if payment.email:
                    send_payment_success_email.delay(payment.email, payment.booking_reference)

                return Response(
                    {"status": "success", "message": "Payment verified successfully"},
                    status=status.HTTP_200_OK
                )
            else:
                payment.status = "Failed"
                payment.save()
                return Response(
                    {"status": "failed", "message": "Payment failed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"status": "failed", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )










# import uuid
# import requests
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Payments
# from .tasks import send_payment_success_email

# CHAPA_API_URL = "https://api.chapa.co/v1/transaction"


# class InitiatePaymentView(APIView):
#     authentication_classes = []  # No authentication required
#     permission_classes = []      # Allow anyone to access

#     def post(self, request):
#         try:
#             # Get data from request
#             amount = request.data.get("amount")
#             email = request.data.get("email")
#             first_name = request.data.get("first_name", "John")
#             last_name = request.data.get("last_name", "Doe")

#             # Validate input
#             if not all([amount, email, first_name, last_name]):
#                 return Response(
#                     {"status": "failed", "message": "All fields are required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Prepare Chapa API request
#             headers = {
#                 "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
#                 "Content-Type": "application/json"
#             }

#             tx_ref = f"tx-{uuid.uuid4()}"  # Unique transaction reference

#             payload = {
#                 "amount": str(amount),
#                 "currency": "ETB",
#                 "email": email,
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "tx_ref": tx_ref,
#                 "callback_url": "https://yourdomain.com/api/payments/verify/",
#                 "return_url": "https://yourdomain.com/payment-success/",
#                 "customization": {
#                     "title": "Payment for Booking",
#                     "description": "Secure payment via Chapa"
#                 }
#             }

#             # Send request to Chapa
#             response = requests.post(f"{CHAPA_API_URL}/initialize", json=payload, headers=headers)
#             chapa_response = response.json()

#             # Check Chapa response
#             if chapa_response.get("status") != "success":
#                 return Response(chapa_response, status=status.HTTP_400_BAD_REQUEST)

#             # Save payment in database
#             Payments.objects.create(
#                 amount=amount,
#                 email=email,
#                 user=None,  # Since no authentication
#                 booking_reference=tx_ref,
#                 status="Pending"
#             )

#             # Return success response
#             return Response({
#                 "status": "success",
#                 "message": "Payment initialized successfully",
#                 "checkout_url": chapa_response["data"]["checkout_url"],
#                 "tx_ref": tx_ref
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"status": "failed", "message": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# class VerifyPaymentView(APIView):
#     authentication_classes = []  # No authentication required
#     permission_classes = []      # Allow anyone to access

#     def get(self, request):
#         try:
#             transaction_id = request.query_params.get("transaction_id")
#             if not transaction_id:
#                 return Response(
#                     {"status": "failed", "message": "Transaction ID is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             headers = {
#                 "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
#                 "Content-Type": "application/json",
#             }

#             # Send verification request to Chapa
#             response = requests.get(f"{CHAPA_API_URL}/verify/{transaction_id}", headers=headers)
#             chapa_response = response.json()

#             # Get payment from DB
#             try:
#                 payment = Payments.objects.get(booking_reference=transaction_id)
#             except Payments.DoesNotExist:
#                 return Response(
#                     {"status": "failed", "message": "Payment not found"},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # Update payment status
#             if chapa_response.get("status") == "success":
#                 payment.status = "Completed"
#                 payment.save()
#                 if payment.email:
#                     send_payment_success_email.delay(payment.email, payment.booking_reference)
#                 return Response(
#                     {"status": "success", "message": "Payment verified successfully"},
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                 payment.status = "Failed"
#                 payment.save()
#                 return Response(
#                     {"status": "failed", "message": "Payment failed"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         except Exception as e:
#             return Response(
#                 {"status": "failed", "message": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# import requests
# import uuid
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# # ============================================
# # 1. INITIATE PAYMENT
# # ============================================
# @csrf_exempt
# def initiate_payment(request):
#     if request.method != "POST":
#         return JsonResponse({"message": "Method not allowed"}, status=405)

#     try:
#         # Get data from the request body
#         amount = request.POST.get("amount")
#         email = request.POST.get("email")
#         first_name = request.POST.get("first_name")
#         last_name = request.POST.get("last_name")

#         if not amount or not email or not first_name or not last_name:
#             return JsonResponse({"message": "Missing required fields"}, status=400)

#         # Generate a unique transaction reference
#         tx_ref = str(uuid.uuid4())

#         # Prepare payload
#         payload = {
#             "amount": amount,
#             "currency": "ETB",  # Change this if needed: GHS, KES, RWF, etc.
#             "email": email,
#             "first_name": first_name,
#             "last_name": last_name,
#             "tx_ref": tx_ref,
#             "callback_url": f"http://127.0.0.1:8000/api/payments/verify/{tx_ref}",
#             "return_url": "http://127.0.0.1:8000/payment-success/",
#             "customization": {
#                 "title": "Ecommerce Payment",
#                 "description": "Payment for selected items",
#             }
#         }

#         # Send request to Chapa API
#         headers = {
#             "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }
#         response = requests.post(settings.CHAPA_INITIALIZE_URL, json=payload, headers=headers)
#         res_data = response.json()

#         # Check for errors from Chapa API
#         if response.status_code != 200:
#             return JsonResponse(res_data, status=response.status_code)

#         return JsonResponse(res_data, status=200)

#     except Exception as e:
#         return JsonResponse({"message": str(e)}, status=500)

# # ============================================
# # 2. VERIFY PAYMENT
# # ============================================
# @csrf_exempt
# def verify_payment(request, reference):
#     try:
#         url = f"{settings.CHAPA_VERIFY_URL}/{reference}"
#         headers = {
#             "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
#         }

#         response = requests.get(url, headers=headers)
#         res_data = response.json()

#         if response.status_code != 200:
#             return JsonResponse(res_data, status=response.status_code)

#         return JsonResponse(res_data, status=200)

#     except Exception as e:
#         return JsonResponse({"message": str(e)}, status=500)
