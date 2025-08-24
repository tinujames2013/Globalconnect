def premium_status(request):
    is_premium = False
    if request.user.is_authenticated:
        # If your CustomUser lives in adminpanel.models
        try:
            is_premium = request.user.check_premium_status()
        except Exception:
            is_premium = getattr(request.user, "is_premium", False)
    return {"IS_PREMIUM": is_premium}
