from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('home',views.home,name='home'),
    path('login',views.login,name='login'),
    path('about',views.about,name='about'),
    path('contact',views.contact,name='contact'),
    path('comingsoon',views.comingsoon,name='comingsoon'),
    path('contactusmail',views.contactusmail,name='contactusmail'),


    path('login',views.login,name='login'),
    path('loginprocess',views.loginprocess,name='loginprocess'),
    path('userlogout',views.userlogout,name='userlogout'),
    path('myaccount',views.myaccount,name='myaccount'),

    
    path('changepassword',views.changepassword,name='changepassword'),
    path('changepasswordprocess',views.changepasswordprocess,name='changepasswordprocess'),

    path('register',views.register,name='register'),
    path('registerprocess',views.registerprocess,name='registerprocess'),

    path('forgetpassword',views.forgetpassword,name='forgetpassword'),
    path('forgotprocess',views.forgotprocess,name='forgotprocess'),

    path('prebuilt',views.prebuilt,name='prebuilt'),
    path('products',views.products,name='products'),
    path('productdetails/<int:id>',views.productdetails,name='productdetails'),
    path('productfilter_category/<int:id>',views.productfilter_category,name='productfilter_category'),
    path('productfilter_brand/<int:id>',views.productfilter_brand,name='productfilter_brand'),
    path('productfilter_price/',views.productfilter_price,name='productfilter_price'),



    path('cartprocess',views.cartprocess,name='cartprocess'),
    path('addtocart/<int:id>',views.addtocart,name='addtocart'),
    path('cart',views.cart,name='cart'),
    path('updatecart',views.updatecart,name='updatecart'),
    path('deletecart/<int:id>',views.deletecart,name='deletecart'),

    path('wishlistcreate/<int:id>',views.wishlistcreate,name='deletecart'),
    path('movetocart/<int:id>',views.movetocart,name='movetocart'),
    path('removewishlist/<int:id>',views.removewishlist,name='removewishlist'),
    path('wishlist',views.wishlist,name='wishlist'),

    path('checkout',views.checkout,name='checkout'),
    path('orderplace',views.orderplace,name='orderplace'),
    path('orderconfirm',views.orderconfirm,name='orderconfirm'),
    path('myorders',views.myorders,name='myorders'),


# Customization starts here

    path('customization',views.cartlistingcustom,name='customization'),
    path('productcustom/<int:id>', views.productlistingcustom),
    path('productcustom/<int:cid>/<int:pid>', views.productlistingcustombyid),
    path('cartdelete/<int:id>', views.cartdelete),
    path('cartaddcustom/<int:id>', views.cartaddcustomprocess, name="categorycreate"),
    path('emptycart', views.emptycart),
    path('customcheckout',views.customcheckout,name='customcheckout'),
    path('customorderplace',views.customorderplace,name='customorderplace'),

# Community Forums

    path('forums',views.forums,name='forums'),
    
    path('forumsrly/<int:id>',views.forums,name='forums'),
    path('forumprocess',views.forumprocess,name='forumprocess'),
]
