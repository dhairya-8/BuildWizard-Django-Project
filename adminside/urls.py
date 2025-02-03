from django.urls import path
from . import views

urlpatterns = [
    
# Login, Forogt Password
    path('',views.login,name='login'),
    path('login',views.login,name='login'),
    path('loginprocess',views.loginprocess,name='loginprocess'),
    path('adminlogout',views.adminlogout,name='adminlogout'),
    path('changepassword',views.changepassword,name='changepassword'),
    path('changepasswordprocess',views.changepasswordprocess,name='changepasswordprocess'),
    path('index',views.index,name='index'),  
    path('forgot',views.forgot,name='forgot'),
    path('forgotprocess',views.forgotprocess,name='forgotprocess'), 
 

# Manage Products
    path('insertproduct',views.insertproduct,name='insertproduct'),
    path('insertproductimage',views.productimage,name='insertproductimage'),
    path('productimageprocess',views.productimageprocess,name='insertproductimageprocess'),
    path('productprocess',views.productprocess,name='productprocess'),
    path('displayproduct',views.displayproduct,name='displayproduct'),
    path('deleteproduct/<int:id>',views.deleteproduct,name='deleteproduct'),
    path('editproduct/<int:id>',views.editproduct,name='editproduct'),
    path('updateproduct',views.updateproduct,name='updateproduct'),

# Brand    
    path('insertbrand',views.insertbrand,name='insertbrand'),
    path('brandprocess',views.brandprocess,name='brandprocess'),
    path('displaybrand',views.displaybrand,name='displaybrand'),
    path('deletebrand/<int:id>',views.deletebrand,name='deletebrand'),
    path('editbrand/<int:id>',views.editbrand,name='editbrand'),
    path('updatebrand',views.updatebrand,name='updatebrand'),

# Categories
    path('insertcategory',views.insertcategory,name='insertcategory'),
    path('categoryprocess',views.categoryprocess,name='categoryprocess'),
    path('displaycategory',views.displaycategory,name='displaycategory'),
    path('deletecategory/<int:id>',views.deletecategory,name='deletecategory'),
    path('editcategory/<int:id>',views.editcategory,name='editcategory'),
    path('updatecategory',views.updatecategory,name='updatecategory'),

# Order
    path('displayorders',views.displayorders,name='displayorders'),
    path('editorders/<int:id>',views.editorders,name='editorders'),
    path('updatestatus',views.updatestatus,name='updatestatus'),
    path('displayorderdetails',views.displayorderdetails,name='displayorderdetails'),
    
# Community Forums
    path('forums',views.forums,name='displayforums'),
    path('deleteforums/<int:id>',views.deleteforums,name='deleteforums'),

    
# Reports
    path('reportproduct_category',views.reportproduct_category,name='reportproduct_category'),
    path('reportproduct_category_process',views.reportproduct_category_process,name='reportproduct_category_process'),
    # path('reportproduct2',views.reportproduct1,name='reportproduct1'),
    path('reportproduct_brand',views.reportproduct_brand,name='reportproduct_brand'),
    path('reportproduct_brand_process',views.reportproduct_brand_process,name='reportproduct_brand_process'),
    path('reportorder_datewise',views.reportorder_datewise,name='reportorder_datewise'),
    path('reportorder_datewise_process',views.reportorder_datewise_process,name='reportorder_datewise_process'),
    path('reportorder_userwise',views.reportorder_userwise,name='reportorder_userwise'),
    path('reportorder_userwise_process',views.reportorder_userwise_process,name='reportorder_userwise_process'),


]
