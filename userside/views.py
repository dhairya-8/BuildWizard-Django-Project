import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator


#DB connection
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 
from adminside.views import DatabaseManager 
db_manager = DatabaseManager() # object of class DatabaseManager
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def about(request):
    return render(request,'user/about.html')

def contact(request):
    return render(request,'user/contact.html')

def comingsoon(request):
    return render(request,'user/comingsoon.html')

def contactusmail(request):
    
    cu1 = request.POST['name']
    cu2 = [request.POST['email'],]
    cu3 = request.POST['phone']
    cu4 = request.POST['subject']
    cu5 = request.POST['message']
    subject = "Greetings From BuildWizard"
    msg = "Hello " + cu1 + "\nWe have seen your keen interest in " + cu4 + ", our team will connect with you shortly on you contact number  " + cu3 + "\n\nThank You for choosing us" + "\n\nRegards" + "\nTeam BuildWizard"
    sender = settings.EMAIL_HOST_USER 
    receiver = [request.POST['email']]
    send_mail(subject,msg,sender,receiver)
    messages.success(request," Mail sent, we will reach you soon ! ")
    return render(request, "user/contact.html")

def login(request):
    return render(request,'user/login.html')

def myaccount(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user id from session
        # cur.execute(''' SELECT * FROM tbl_ordermaster WHERE user_id = {} '''.format(uid))
        myaccount_query = ''' SELECT * FROM tbl_ordermaster WHERE user_id = %s '''
        data = db_manager.fetch_all(myaccount_query, (uid,))
        
        return render(request, 'user/myaccount.html', {'od': data})  
    else:
        return redirect(login)
    # return render(request,'user/myaccount.html')
 
def loginprocess(request):
    # Get textbox values
    l1 = request.POST['email']
    l2 = request.POST['password']
    loginprocess_query = "SELECT * FROM tbl_user WHERE user_email = %s AND user_password = %s"
    data = db_manager.fetch_one(loginprocess_query, (l1,l2))
    print(f"login data -----> {data}")
    if data is not None:

        if len(data) > 0:
            #fetch data from DB
            user_db_id = data[0] #fetching id of user
            user_db_email = data[3]
            user_db_name = data[1]
            #storing user's info in session
            request.session['user_id'] = user_db_id
            request.session['user_name'] = user_db_name
            #storing user's info in cookie
            response = redirect(home)
            response.set_cookie('user_id',user_db_id)
            response.set_cookie('user_name',user_db_name)
            return response
        else:
            messages.warning(request, 'Login Failed !')
            return render(request,'user/login.html')
    messages.warning(request, 'Login Failed !')
    return render(request,'user/login.html')

def home(request):
    if 'user_name' in request.COOKIES and request.session.has_key('user_name'):
        user_emails = request.session['user_name']
        user_emailc = request.COOKIES['user_name']
        print("Session name is :",  user_emails)
        print("Cookie name is :",  user_emailc) 
        return render(request, 'user/home.html')
    else:
        return render(request, 'user/home.html')
    
def userlogout(request):
    del request.session['user_name']
    del request.session['user_id']
    response = redirect(home)
    response.delete_cookie('user_id')
    response.delete_cookie('user_name')
    return response

def changepassword(request):
    return render(request, 'user/myaccount.html')

def changepasswordprocess(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        user_id = request.session['user_id']
        print(f"session id is -> {user_id}")
        opass = request.POST['old'] # Getting values from form
        npass = request.POST['new']
        cpass = request.POST['confirm']
        # Fetching Old Password from DB
        changepasswordprocess_query = "SELECT * FROM tbl_user WHERE user_id = %s "
        db_data = db_manager.fetch_one(changepasswordprocess_query, (user_id,))
        if db_data is not None:
            if len(db_data) > 0:
                oldpassword_db = db_data[4]
                # Comparing Old Password with DB's Old Password
                if opass == oldpassword_db:
                    # Comparing New and Confirm Password
                    if npass != cpass:
                        messages.warning(request, 'New and Confirm Password did not matched !')
                        return render(request, 'user/myaccount.html')
                    else:
                        update_query = "UPDATE tbl_user SET user_password = %s WHERE user_id = %s "
                        db_manager.execute_query(update_query, (npass,user_id))
                        messages.success(request, 'Password Changed Successfully !')
                        return render(request, 'user/myaccount.html')
                else:
                    messages.warning(request, 'Old Password did not matched !')
                    return render(request, 'user/myaccount.html')
            else:
                redirect(request, login)
        else:
            redirect(request, login)
    else:
        return redirect(login)

def register(request):
    return render(request, 'user/register.html')

def registerprocess(request):
    # Get textbox values
    r1 = request.POST['name']
    r2 = request.POST['gender']
    r3 = request.POST['email']
    r4 = request.POST['password']
    r5 = request.POST['number']
    r6 = request.POST['address']

    # Check if the email already exists
    check_email_query = "SELECT * FROM tbl_user WHERE user_email = %s"
    email_exists = db_manager.fetch_one(check_email_query, (r3,)) 
    if email_exists is not None:  
        print(f"email already registered --->{email_exists}")
        messages.warning(request, "This email address is already registered.")
        return redirect('login')  # Redirect back to the registration page
    
    try:
        registerprocess_query = "INSERT INTO tbl_user (user_name, user_gender, user_email, user_password, user_mobile, user_address) VALUES (%s,%s,%s,%s,%s,%s)"
        db_manager.execute_query(registerprocess_query, (r1,r2,r3,r4,r5,r6))
        messages.success(request, 'Account has been created !')
        return redirect(login)
    
    except Exception as e:
        messages.warning(request, "An error occurred while creating your account. Please try again.")
        return redirect('register')


def forgetpassword(request):
    return render(request,'user/forgetpassword.html')

def forgotprocess(request):

    f1 = request.POST['email']
    forgotprocess_query = "SELECT * FROM tbl_user WHERE user_email = %s "
    db_user = db_manager.fetch_one(forgotprocess_query, (f1,))
     
    user_email = db_user[3]
    # Checking if Email is registered or not
    if f1 == user_email:
        subject = "Forgot Password"
        user_name = db_user[1]
        user_password = db_user[4]
        msg = "Hello, " + user_name + "\nWe have got your request for forgot password \n" + "Your current password is : " + user_password + "\n Kindly change it for security purpose" + "\n\nThanks & Regards" + "\nTeam - BuildWizard"
        sender = settings.EMAIL_HOST_USER 
        receiver = [request.POST['email']]
        send_mail(subject,msg,sender,receiver)
        messages.success(request," Mail sent, check inbox ")
        return redirect(forgetpassword)
    else:
        messages.error(request, "Email does not exist !")
        return redirect(forgetpassword)

def prebuilt(request):
    return render(request,'user/prebuilt.html')

def products(request):
    display_products_query = ''' 
SELECT
    `tbl_product`.`product_id`,
    `tbl_product`.`product_name`,
    `tbl_product`.`product_details`,
    `tbl_product`.`product_price`,
    `tbl_category`.`category_name`,
    `tbl_brand`.`brand_name`,
    `tbl_productimages`.`image_name`
FROM
    `buildwizard`.`tbl_product`
    INNER JOIN `buildwizard`.`tbl_category` 
        ON (`tbl_category`.`category_id` = `tbl_product`.`category_id`)
    INNER JOIN `buildwizard`.`tbl_brand` 
        ON (`tbl_brand`.`brand_id` = `tbl_product`.`brand_id`)
    LEFT JOIN `buildwizard`.`tbl_productimages` 
        ON (`tbl_productimages`.`product_id` = `tbl_product`.`product_id` AND `tbl_productimages`.`image_order` = 1);
'''
    data = db_manager.fetch_all(display_products_query)
    print (f'products data -> {data}')
  
    # Pagination 
    paginator = Paginator(data, 9)
    page_number = request.GET.get("page")
    pgo = paginator.get_page(page_number)
    print(pgo)
    start_index = pgo.start_index()  # Start index for the current page.
    end_index = pgo.end_index()      # End index for the current page.
    
    # Category
    display_category_query = "SELECT * FROM tbl_category"
    cdata = db_manager.fetch_all(display_category_query) 
    
    # Brand
    display_brand_query = "SELECT * FROM tbl_brand"
    bdata = db_manager.fetch_all(display_brand_query) 
    
    return render(request,'user/products.html',{'mydata':pgo,'mycdata':cdata,'mybdata':bdata, 'start_index': start_index, 'end_index': end_index,})

def productfilter_category(request,id):
    # Filter for Categories
    productfilter_category_query = "SELECT * FROM tbl_product  WHERE category_id = %s"
    data = db_manager.fetch_all(productfilter_category_query,(id,)) 
    print(list(data))

    display_category_query = ("SELECT * FROM tbl_category")
    cdata = db_manager.fetch_all(display_category_query) 
    print(list(cdata))
    
    display_brand_query = "SELECT * FROM tbl_brand"
    bdata = db_manager.fetch_all(display_brand_query)
    print(list(bdata))
     
    return render(request,'user/products.html',{'mydata':data,'mycdata':cdata,'mybdata':bdata})

def productfilter_brand(request,id):
    # Filter for Brand
    productfilter_brand_query = "SELECT * FROM tbl_product  WHERE brand_id = %s"
    data = db_manager.fetch_all(productfilter_brand_query, (id,)) 
    print(list(data))

    display_category_query = "SELECT * FROM tbl_category"
    cdata = db_manager.fetch_all(display_category_query) 
    print(list(cdata))
     
    display_brand_query = "SELECT * FROM tbl_brand"
    bdata = db_manager.fetch_all(display_brand_query)
    print(list(bdata))
     
    return render(request,'user/products.html',{'mydata':data,'mycdata':cdata,'mybdata':bdata})

def productfilter_price(request):
    # Filter for Price Range
    p1 = request.GET.get('p1')
    p2 = request.GET.get('p2')
    productfilter_price_query = """
    SELECT * FROM tbl_product 
    WHERE CAST(product_price AS DECIMAL(10, 2)) BETWEEN %s AND %s
"""
    data = db_manager.fetch_all(productfilter_price_query, (p1,p2))
    print(f"price filter products--->{data}")
    print(list(data))
    
    display_category_query = "SELECT * FROM tbl_category"
    cdata = db_manager.fetch_all(display_category_query) 
    print(list(cdata))
     
    display_brand_query = "SELECT * FROM tbl_brand"
    bdata = db_manager.fetch_all(display_brand_query)
    print(list(bdata))
     
    return render(request,'user/products.html',{'mydata':data,'mycdata':cdata,'mybdata':bdata})

    # , `tbl_product`.`product_image`
def productdetails(request,id):
    print ("Product selected is ",id)
    productdetails_query = ''' SELECT
    `tbl_product`.`product_id`
    , `tbl_product`.`product_name`
    , `tbl_product`.`product_details`
    , `tbl_product`.`product_price`
    , `tbl_category`.`category_name`
    , `tbl_brand`.`brand_name`
    , `tbl_productimages`.`image_name`

FROM
    `buildwizard`.`tbl_category`
    INNER JOIN `buildwizard`.`tbl_product` 
        ON (`tbl_category`.`category_id` = `tbl_product`.`category_id`)
    INNER JOIN `buildwizard`.`tbl_brand` 
        ON (`tbl_brand`.`brand_id` = `tbl_product`.`brand_id`)
    LEFT JOIN `buildwizard`.`tbl_productimages`  
        ON `tbl_productimages`.`product_id` = `tbl_product`.`product_id`
        AND `tbl_productimages`.`image_order` = 1  

WHERE `tbl_product`.`product_id` = %s; '''

    data = db_manager.fetch_one(productdetails_query, (id,))
    print (list(data))
    productdetails_image_query = "SELECT * FROM tbl_productimages WHERE product_id =%s"
    imgdata = db_manager.fetch_all(productdetails_image_query, (id,))
    print(list(imgdata))

    return render(request, 'user/productdetails.html', {'mydata': data,'myimgdata': imgdata,})

def addtocart(request,id):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user_id from session
        pid = id
        qty = 1
        addtocart_query = "INSERT INTO tbl_cart (product_id, user_id, product_qty) VALUES (%s,%s,%s)"
        db_manager.execute_query(addtocart_query, (pid,uid,qty))
        print ("Added to cart")
        return redirect(cart)
    else:
        return redirect(login)

def cartprocess(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user_id from session
        pid = request.POST['p_id'] # taking product_id 
        qty = request.POST['qty']  # taking quantity of the product

        cartprocess_query = "INSERT INTO tbl_cart (product_id, user_id, product_qty) VALUES (%s,%s,%s)"
        db_manager.execute_query(cartprocess_query, (pid,uid,qty))
        print ("Added to cart")
        return redirect(cart)
    else:
        return redirect(login)
    
def cart(request):
    if request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user id from session
        cart_display_query = '''SELECT
    tbl_cart.cart_id,
    tbl_product.product_id,
    tbl_product.product_name,
    tbl_product.product_price,
    tbl_cart.product_qty,
    tbl_productimages.image_name,  -- Change this to match the image_name from the latest query
    (tbl_product.product_price * tbl_cart.product_qty) AS tot_price_times_qty,
    tbl_category.category_name,
    tbl_brand.brand_name
FROM
    buildwizard.tbl_cart
    INNER JOIN buildwizard.tbl_product 
        ON tbl_product.product_id = tbl_cart.product_id
    INNER JOIN buildwizard.tbl_category 
        ON tbl_category.category_id = tbl_product.category_id
    INNER JOIN buildwizard.tbl_brand 
        ON tbl_brand.brand_id = tbl_product.brand_id
    LEFT JOIN buildwizard.tbl_productimages 
        ON tbl_productimages.product_id = tbl_product.product_id AND tbl_productimages.image_order = 1
WHERE 
    tbl_cart.user_id = %s;'''
        
        data = db_manager.fetch_all(cart_display_query, (uid,))
        countevalue = len(data)  
        #Sum(Cart Grand Total)
        res = sum(i[6] for i in data) 
        return render(request,'user/cart.html',{'mydata':data,'count':countevalue,'total':res})
    else:
        return redirect(login)
    
def wishlistcreate(request,id):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user_id from session
        wishlistcreate_query = "INSERT INTO tbl_wishlist (product_id, user_id) VALUES (%s,%s)"
        db_manager.execute_query(wishlistcreate_query, (id,uid))
        print ("Added to wishlist")
        return redirect(wishlist)
    else:
        return redirect(login)
    
def wishlist(request):
    if request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user_id from session
        wishlist_display_query = '''SELECT
    `tbl_wishlist`.`wishlist_id`,
    `tbl_product`.`product_name`,
    `tbl_product`.`product_price`,
    `tbl_productimages`.`image_name`,  -- Changed from `tbl_product`.`product_image` to `tbl_productimages`.`image_name`
    `tbl_product`.`product_id`
FROM
    `tbl_product`
    INNER JOIN `tbl_wishlist` 
        ON (`tbl_product`.`product_id` = `tbl_wishlist`.`product_id`)
    LEFT JOIN `tbl_productimages`  -- Added LEFT JOIN to include the product images
        ON `tbl_productimages`.`product_id` = `tbl_product`.`product_id` AND `tbl_productimages`.`image_order` = 1
WHERE 
    `tbl_wishlist`.`user_id` = %s;'''
        data = db_manager.fetch_all(wishlist_display_query, (uid,))
        return render(request, 'user/wishlist.html',{'mydata':data})
    else:
        return redirect(login)
    
def movetocart(request,id):
    if request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user_id from session
        id=id
        insertintocart_query = "INSERT INTO `tbl_cart`(`user_id`,`product_id`,`product_qty`) VALUES (%s,%s,%s)"
        db_manager.execute_query(insertintocart_query, (uid,id,1))
        deletefromwishlist_query = "delete from tbl_wishlist where user_id = %s and product_id = %s "
        db_manager.execute_query(deletefromwishlist_query, (uid,id))
        return redirect(cart)
    else:
        return redirect(login)

def removewishlist(request,id):
    print ("Deleted product is",id)
    removewishlist_query = "DELETE FROM tbl_wishlist WHERE wishlist_id = %s"
    db_manager.execute_query(removewishlist_query, (id,))
    return redirect(wishlist)
    
def updatecart(request):
    if request.session.has_key('user_id'):
        if request.method == 'POST':
            print(request.POST)
            cid = request.POST['cid']
            qty = request.POST['qty']

            updatecart_query = "UPDATE tbl_cart SET product_qty =%s WHERE cart_id =%s"
            db_manager.execute_query(updatecart_query, (qty,cid))
            return redirect(cart)
        else:
            return redirect(cart)
    else:
        return redirect(login)

def deletecart(request,id):
    print ("Deleted product is",id)
    deletecart_query = "DELETE FROM tbl_cart WHERE cart_id =%s"
    db_manager.execute_query(deletecart_query, (id,))
    return redirect(cart)

def checkout(request):
    
    if request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user id from session
        checkout_query = '''SELECT
            tbl_cart.cart_id,
            tbl_product.product_id,
            tbl_product.product_name,
            tbl_product.product_price,
            tbl_cart.product_qty,
            tbl_productimages.image_name,  -- Updated to use the image_name from the latest query
            (tbl_product.product_price * tbl_cart.product_qty) AS tot_price_times_qty,
            tbl_category.category_name,
            tbl_brand.brand_name

            FROM
            buildwizard.tbl_cart
                INNER JOIN buildwizard.tbl_product 
                    ON tbl_product.product_id = tbl_cart.product_id
                INNER JOIN buildwizard.tbl_category 
                    ON tbl_category.category_id = tbl_product.category_id
                INNER JOIN buildwizard.tbl_brand 
                    ON tbl_brand.brand_id = tbl_product.brand_id
                LEFT JOIN buildwizard.tbl_productimages 
                    ON tbl_productimages.product_id = tbl_product.product_id AND tbl_productimages.image_order = 1
            WHERE 
                tbl_cart.user_id = %s;'''
        
        data = db_manager.fetch_all(checkout_query, (uid,))
        print(list(data))
        countevalue = len(data)  
        #Sum(Cart Grand Total)
        res = sum(i[6] for i in data) 
        return render(request,'user/checkout.html',{'mydata':data,'count':countevalue,'total':res})
    else:
        return redirect(login)

def orderplace(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        order_date = datetime.datetime.now().strftime ("%Y-%m-%d")
        order_status = "Confirmed"
        userid = request.session['user_id']
        mop = request.POST['mop']
        sname = request.POST['name']
        smobile = request.POST['mnumber']
        saddress = request.POST['address']
       
        # Get the last inserted order id
        orderid = db_manager.execute_query("INSERT INTO tbl_ordermaster(order_date,order_status,user_id,mode_of_payment,shipping_name,shipping_mobile,shipping_address) VALUES (%s,%s,%s,%s,%s,%s,%s)", (order_date,order_status,userid,mop,sname,smobile,saddress))

        print(f"Fetching order ID:-----------> {orderid}")

        
        #Order details insertion

        uid = request.session['user_id']
        # Fetch order details
        product_details = db_manager.fetch_all(''' SELECT
              tbl_cart.product_id
            , tbl_product.product_price
            , tbl_cart.product_qty
        FROM
            tbl_product
            INNER JOIN tbl_cart 
                ON (tbl_product.product_id = tbl_cart.product_id) WHERE tbl_cart.user_id = %s''', (uid,))
        
        # Insert in order details

        for i in product_details:
            
            pid = i[0]
            price = i[1]
            qty = i[2]
            db_manager.execute_query("INSERT INTO tbl_orderdetails(order_id,product_id,quantity,price) VALUES (%s,%s,%s,%s)", (orderid,pid,qty,price))

        # Remove items from cart
        db_manager.execute_query("DELETE FROM tbl_cart WHERE user_id = %s", (uid,))
        return redirect(orderconfirm)
    else:
        return redirect(login)

def orderconfirm(request):
    return render(request,"user/orderconfirm.html")

def myorders(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user id from session
        data = db_manager.fetch_all(''' SELECT * FROM tbl_ordermaster WHERE user_id = %s ''', (uid,))
        
        return render(request, 'user/myaccount.html', {'od': data})  
    else:
        return redirect(login)

# Customization starts here

def cartlistingcustom(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user id from session
        data = db_manager.fetch_all('''SELECT
        tbl_customcart.customcart_id
        , tbl_product.product_name
        , tbl_product.product_price
        , tbl_customcart.product_qty
        , tbl_category.category_name
        , tbl_customcart.user_id
        , tbl_customcart.product_id
        , tbl_product.product_price * tbl_customcart.product_qty AS tot_price_times_qty
    
        FROM
            tbl_product
            INNER JOIN tbl_customcart 
            ON (tbl_product.product_id = tbl_customcart.product_id)
        INNER JOIN tbl_category 
            ON (tbl_category.category_id = tbl_product.category_id) WHERE tbl_customcart.user_id = %s ''', (uid,))
        
        #return list(data)
         
        data1 = db_manager.fetch_all('''select * from tbl_category ''')
        
        countevalue = len(data)
        print("------------------")
        print(countevalue)
    
        #Sum(Cart Grand Total)
        res = sum(i[7] for i in data) 
        print(res)
        return render(request, 'user/customization.html', {'mydata': data,'mycat':data1,'count':countevalue,'total':res})
    else:
        return redirect(login)

def cartaddcustomprocess(request,id):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        userid = request.session['user_id'] # taking user id from session
        id = id
        db_manager.execute_query("INSERT INTO `tbl_customcart`(`user_id`,`product_id`,`product_qty`) VALUES (%s,%s,%s)", (userid,id,1))
        return redirect(cartlistingcustom) 
    else:
        return redirect(login)
    
def cartdelete(request,id):
    id = id
    db_manager.execute_query("delete from `tbl_customcart` where `customcart_id` = {} ", (id,))
    return redirect(cartlistingcustom)

def emptycart(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        userid = request.session['user_id'] # taking user id from session
        db_manager.execute_query("delete from `tbl_customcart` where `user_id` = %s ", (userid,))
        return redirect(cartlistingcustom)
    else:
        return redirect(login)
    
def productlistingcustom(request,id):
    data = db_manager.fetch_all('''SELECT * FROM `tbl_product` where `category_id` = %s ''', (id,))    
    print(list(data))    
    data1 = db_manager.fetch_one(''' select * from tbl_category where category_id = {}''', (id,))
    
    return render(request, 'user/customproduct.html', {'mydata': data,'categoryname':data1})

def productlistingcustombyid(request,cid,pid):
    cid = cid
    pid = pid
    data = db_manager.fetch_all('''SELECT
    `tbl_product`.*
    , `tbl_compatibility`.`compatibility_product_id`
    
FROM
    `tbl_product`
    INNER JOIN `tbl_compatibility` 
        ON (`tbl_product`.`product_id` = `tbl_compatibility`.`compatibility_product_id`)
            
         WHERE `tbl_compatibility`.`product_id`= %s and `tbl_product`.`category_id` = %s''', (pid,cid))
    
    countd1 = len(data)
    data1 = db_manager.fetch_one(''' select * from tbl_category where category_id = %s''', (cid,))    
    countd2 = len(data1)
    #return list(data)
    print(list(data1))
    return render(request, 'user/customproduct.html', {'mydata': data,'categoryname':data1,'c1':countd1,'c2':countd2})

def customcheckout(request):
    
    if request.session.has_key('user_id'):
        uid = request.session['user_id'] # taking user id from session
        data = db_manager.fetch_all('''SELECT
    `tbl_customcart`.`customcart_id`
    , `tbl_product`.`product_id`
    , `tbl_product`.`product_name`
    , `tbl_product`.`product_price`
    , `tbl_customcart`.`product_qty`
    , `tbl_product`.`product_image`
    , tbl_product.product_price * tbl_customcart.product_qty AS tot_price_times_qty

FROM
    `buildwizard`.`tbl_product`
    INNER JOIN `buildwizard`.`tbl_customcart` 
        ON (`tbl_product`.`product_id` = `tbl_customcart`.`product_id`) WHERE `tbl_customcart`.`user_id` = %s ''', (uid,))
        
        res = sum(i[6] for i in data) 
        countevalue = len(data)
        return render(request,'user/customcheckout.html',{'mydata':data,'subtotal':res,'count':countevalue})
    else:
        return redirect(login)

# 
def customorderplace(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        order_date = datetime.datetime.now().strftime("%Y-%m-%d")
        order_status = "Confirmed"
        userid = request.session['user_id']
        mop = request.POST['mop']
        sname = request.POST['name']
        smobile = request.POST['mnumber']
        saddress = request.POST['address']

        # Insert order into tbl_ordermaster and get the last inserted order ID
        orderid = db_manager.execute_query(
            "INSERT INTO tbl_ordermaster(order_date, order_status, user_id, mode_of_payment, shipping_name, shipping_mobile, shipping_address) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
            (order_date, order_status, userid, mop, sname, smobile, saddress)
        )

        # Retrieve custom cart details
        uid = request.session['user_id']
        data = db_manager.fetch_all(''' 
            SELECT
                tbl_customcart.product_id,
                tbl_product.product_price,
                tbl_customcart.product_qty
            FROM
                tbl_product
            INNER JOIN tbl_customcart 
                ON tbl_product.product_id = tbl_customcart.product_id 
            WHERE tbl_customcart.user_id = %s
        ''', (uid,))

        # Insert order details into tbl_orderdetails
        for i in data:
            pid = i[0]
            price = i[1]
            qty = i[2]
            print(f"Inserting order detail - OrderID: {orderid}, ProductID: {pid}, Quantity: {qty}, Price: {price}")
            db_manager.execute_query(
                "INSERT INTO tbl_orderdetails(order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", 
                (orderid, pid, qty, price)
            )

        # Clear the user's custom cart
        db_manager.execute_query("DELETE FROM tbl_customcart WHERE user_id = %s", (uid,))

        return redirect(orderconfirm)
    else:
        return redirect(login)

# Community Forums
    
def forums(request):
    data = db_manager.fetch_all('''SELECT
    tbl_forums.forum_id
    ,tbl_forums.forum_msg
    ,tbl_forums.forum_date
    ,tbl_user.user_name
    ,tbl_forums.is_rly
    ,tbl_forums.rly_id
    FROM
    tbl_user
    INNER JOIN tbl_forums 
        ON (tbl_user.user_id = tbl_forums.user_id);''')
    
    return render(request,'user/forums.html',{'mydata':data})

def forumprocess(request):
    if 'user_id' in request.COOKIES and request.session.has_key('user_id'):
        uid = request.session['user_id']
        forum_date = datetime.datetime.now().strftime ("%Y-%m-%d")
        msg = request.POST['message']
         
        isrly = request.POST['isrly']
        if isrly == 0:
            rly = "false"
        else:
            rly = "true"
        db_manager.execute_query("INSERT INTO tbl_forums(forum_msg,forum_date,user_id,is_rly,rly_id) VALUES(%s,%s,%s,%s,%s)", (msg,forum_date,uid,rly,isrly))
        return redirect(forums)
    else:
        return redirect(login)