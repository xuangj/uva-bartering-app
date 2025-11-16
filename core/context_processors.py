from core.models import Trade


# Calculate pending trades
def pending_trades_count(request):
   if request.user.is_authenticated:
       count = Trade.objects.filter(
           receiver=request.user,
           status="Pending"
       ).count()
   else:
       count = 0
  
   return {"pending_trades_count": count}