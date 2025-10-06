import json
import base64
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import Payment

def get_mpesa_access_token():
    """Get OAuth access token from M-Pesa API"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    
    if settings.MPESA_ENVIRONMENT == 'sandbox':
        api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        api_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Error getting M-Pesa token: {e}")
        return None

@login_required
def upgrade_view(request):
    """Display premium upgrade page"""
    return render(request, 'payments/upgrade.html', {
        'amount': 87,
        'user': request.user,
    })

@login_required
def initiate_payment(request):
    """Initiate STK Push for M-Pesa payment"""
    if request.method != 'POST':
        return redirect('payments:upgrade')
    
    phone_number = request.POST.get('phone_number', '').strip()
    
    # Validate phone number
    if not phone_number:
        messages.error(request, 'Please provide a phone number.')
        return redirect('payments:upgrade')
    
    # Format phone number
    phone_number = phone_number.replace('+', '').replace(' ', '')
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    if not phone_number.startswith('254') or len(phone_number) != 12:
        messages.error(request, 'Invalid phone number. Use format: 254XXXXXXXXX')
        return redirect('payments:upgrade')
    
    # Get access token
    access_token = get_mpesa_access_token()
    if not access_token:
        messages.error(request, 'Payment service unavailable. Please try again later.')
        return redirect('payments:upgrade')
    
    # Prepare STK Push request
    if settings.MPESA_ENVIRONMENT == 'sandbox':
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    else:
        api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    
    # Generate password
    password_str = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode('utf-8')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': 87,
        'PartyA': phone_number,
        'PartyB': shortcode,
        'PhoneNumber': phone_number,
        'CallBackURL': settings.MPESA_CALLBACK_URL,
        'AccountReference': f'Kitabu-{request.user.username}',
        'TransactionDesc': 'Kitabu Premium Upgrade',
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get('ResponseCode') == '0':
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                phone_number=phone_number,
                merchant_request_id=result['MerchantRequestID'],
                checkout_request_id=result['CheckoutRequestID'],
                status='pending'
            )
            
            messages.success(request, 'Payment request sent! Please check your phone and enter your M-Pesa PIN.')
            return render(request, 'payments/payment_pending.html', {
                'payment': payment,
                'phone_number': phone_number,
            })
        else:
            messages.error(request, f"Payment failed: {result.get('ResponseDescription', 'Unknown error')}")
            return redirect('payments:upgrade')
    
    except requests.exceptions.RequestException as e:
        print(f"M-Pesa API Error: {e}")
        messages.error(request, 'Payment request failed. Please try again.')
        return redirect('payments:upgrade')

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa callback after payment"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        callback_data = json.loads(request.body.decode('utf-8'))
        
        # Extract key data from callback
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        merchant_request_id = stk_callback.get('MerchantRequestID')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        
        # Find payment record
        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
        
        if not payment:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Store full callback
        payment.callback_response = callback_data
        
        if result_code == 0:
            # Payment successful
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = item.get('Value')
                elif item.get('Name') == 'TransactionDate':
                    trans_date_str = str(item.get('Value'))
                    payment.transaction_date = datetime.strptime(trans_date_str, '%Y%m%d%H%M%S')
            
            payment.status = 'completed'
            payment.save()
            
            # Activate premium for user
            user = payment.user
            user.is_premium = True
            user.premium_activated_at = timezone.now()
            user.save()
            
        else:
            # Payment failed
            payment.status = 'failed'
            payment.save()
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def payment_status(request, payment_id):
    """Check payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return render(request, 'payments/payment_status.html', {
        'payment': payment,
    })