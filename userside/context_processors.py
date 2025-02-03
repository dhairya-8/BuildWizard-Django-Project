from .views import db_manager  # Adjust according to your import path

def cart_count(request):
    cart_count = 0  # Default value to be safe
    if request.session.has_key('user_id'):
        uid = request.session['user_id']
        count_query = 'SELECT COUNT(*) FROM tbl_cart WHERE tbl_cart.user_id = %s'
        count_data = db_manager.fetch_one(count_query, (uid,))
        if count_data:
            cart_count = count_data[0]  # Adjust according to the result structure
    
    return {
        'cart_count': cart_count
    }

def wishlist_count (request):
    wishlist_count = 0 
    if request.session.has_key('user_id'):
        uid = request.session['user_id']
        count_query = 'SELECT COUNT(*) FROM tbl_wishlist WHERE tbl_wishlist.user_id = %s'
        count_data = db_manager.fetch_one(count_query, (uid,))
        if count_data:
            wishlist_count = count_data[0]

    return {
        'wishlist_count': wishlist_count
    }