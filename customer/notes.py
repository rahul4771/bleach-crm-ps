customer_cart = CustomerCart.objects.prefetch_related(Prefetch('cart_service',queryset=CartService.objects.filter(is_active=True).prefetch_related(Prefetch('cart_service_floor',queryset=CartServiceFloor.objects.all(),to_attr='cart_service_floors')),to_attr='cart_services'),Prefetch('cart_schedule',queryset=CartSchedule.objects.filter(is_active=True),to_attr='cart_schedules')).get(id=evaluation_id_encrypted)

for cart_service in customer_cart.cart_services:
    if cart_service.cart_service_floors:
		for floor in cart_service.cart_service_floors:
            floor.delete()
            
    cart_service.delete()

for cart_schedule in customer_cart.cart_schedules:
    cart_schedule.delete()

customer_cart.is_scheduled = False
customer_cart.total_cost = 0
customer_cart.save()
