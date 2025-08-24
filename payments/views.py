import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.contrib import messages
from payments.models import Payment


# Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def dashboard(request):
    """Payment dashboard"""
    return render(request, 'payments/base.html')


@login_required
def upgrade(request):
    """Step 1: Create Razorpay Order"""
    amount = 50000  # ₹500 in paise
    order = client.order.create(dict(
        amount=amount,
        currency="INR",
        payment_capture="0"  # we will capture after verification
    ))

    # Save order in DB
    Payment.objects.create(
        user=request.user,
        order_id=order["id"],
        amount=amount,
        currency="INR",
        status="created",
    )

    return render(request, "payments/checkout.html", {
        "order_id": order["id"],
        "key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "currency": "INR",
        "user_email": request.user.email,
        "user_name": request.user.username,
    })


@csrf_exempt
def verify(request):
    """Step 2: Verify Razorpay Signature and Capture Payment"""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    try:
        payment = Payment.objects.get(order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        return HttpResponseBadRequest("Payment not found")

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature
    }

    try:
        # Verify Razorpay signature
        client.utility.verify_payment_signature(params_dict)

        # ✅ Capture payment (important: amount in paise)
        client.payment.capture(razorpay_payment_id, payment.amount)

        # Update payment record
        payment.payment_id = razorpay_payment_id
        payment.signature = razorpay_signature
        payment.status = "paid"
        payment.save(update_fields=["payment_id", "signature", "status"])

        # Upgrade user to premium
        if hasattr(payment.user, "activate_premium"):
            payment.user.activate_premium(duration_days=365)
        else:
            # fallback if you use a profile model
            payment.user.profile.is_premium = True
            payment.user.profile.save()

        messages.success(request, "🎉 Payment successful! You are now a Premium member.")
        return redirect("payments:success")

    except razorpay.errors.SignatureVerificationError:
        payment.status = "failed"
        payment.save(update_fields=["status"])
        messages.error(request, "❌ Payment verification failed. Try again.")
        return redirect("payments:failed")


@login_required
def success(request):
    return render(request, "payments/success.html")


@login_required
def failed(request):
    return render(request, "payments/failed.html")

@login_required
def plans(request):
    """Show available subscription plans"""
    return render(request, "payments/plans.html")

@login_required
def transactions(request):
    # Fetch only the logged-in user's payments
    payments = Payment.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "payments": payments
    }
    return render(request, "payments/transactions.html", context)