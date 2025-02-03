from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.mail import send_mail
import pandas as pd
from datetime import datetime


#DB connection
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import mysql.connector as mcdb
from mysql.connector import Error

class DatabaseManager:
    
    def __init__(self, host='localhost', user='root', password='root', database='buildwizard', port=3308):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connection_open(self):
        """Open a new database connection if not already open."""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mcdb.connect(
                    host=self.host, 
                    user=self.user, 
                    password=self.password,
                    database=self.database,
                    port=self.port
                )
                if self.connection.is_connected():
                    print("\n*********************[START]************************\n\nDatabase connected successfully!")
            except Error as e:
                raise Exception(f"Unable to connect to database: {e}")

    def connection_close(self):
        """Close the database connection."""
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            print("Database closed successfully!\n\n**********************[END]***********************")

    def execute_query(self, query, data=None):
        """Execute a single query (INSERT, UPDATE, DELETE)."""
        self.connection_open()
        last_inserted_id = None  # Initialize to None
        cursor = None  # Initialize cursor here
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            if query.strip().lower().startswith("insert"):
                last_inserted_id = cursor.lastrowid  # Capture the last inserted ID
            self.connection.commit()
            print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()  # Close cursor inside finally
            self.connection_close()
        return last_inserted_id  # Return the last inserted ID if applicable

    def fetch_all(self, query, data=None):
        """Fetch all results from a SELECT query."""
        self.connection_open()
        results = None
        cursor = None  # Initialize cursor here
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            results = cursor.fetchall()
            print("Query executed successfully, fetched all results.")
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            if cursor:
                cursor.close()  # Close cursor inside finally
            self.connection_close()
        return results

    def fetch_one(self, query, data=None):
        """Fetch a single result from a SELECT query."""
        self.connection_open()
        result = None
        cursor = None  # Initialize cursor here
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            result = cursor.fetchone()
            print("Query executed successfully, fetched one result.")
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            if cursor:
                cursor.close()  # Close cursor inside finally
            self.connection_close()
        return result
    
db_manager = DatabaseManager() # object of class DatabaseManager

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Login, Forgot Password 
def login(request):
    return render(request,'admin/login.html')

def index(request):
    if 'admin_name' in request.COOKIES and request.session.has_key('admin_name'):
        admin_emails = request.session['admin_name']
        admin_emailc = request.COOKIES['admin_name']
        print("Session name is :",  admin_emails)
        print("Cookie name is :",  admin_emailc)
        return render(request, 'admin/index.html')
    else:
        return redirect(login)

def loginprocess(request):
    # Get textbox values
    l1 = request.POST['email']
    print(l1) 
    l2 = request.POST['password']
    print(l2)
    login_query = "select * from tbl_admin where admin_email = %s and admin_password = %s"
    db_data = db_manager.fetch_one(login_query, (l1,l2))
    print("login--------->",db_data)
    if db_data is not None:

        if len(db_data) > 0:
            #fetch data from DB
            admin_db_id = db_data[0] #fetching id of admin
            admin_db_name = db_data[1]
            admin_db_email = db_data[2]
            #storing admin's info in session
            request.session['admin_id'] = admin_db_id
            request.session['admin_name'] = admin_db_name
    
            #storing admin's info in cookie
            response = redirect(index)
            response.set_cookie('admin_id',admin_db_id)
            response.set_cookie('admin_name',admin_db_name)
            return response
        else:
            messages.warning(request, 'Login Failed, Incorrect Password !')
            return render(request,'admin/login.html')
    messages.warning(request, 'Login Failed, something went wrong !')
    return render(request,'admin/login.html')

    
def adminlogout(request):
    del request.session['admin_name']
    del request.session['admin_id']
    response = redirect(login)
    response.delete_cookie('admin_id')
    response.delete_cookie('admin_name')
    
    return response

def changepassword(request):
    return render(request, 'admin/changepassword.html')

def changepasswordprocess(request):
    if 'admin_id' in request.COOKIES and request.session.has_key('admin_id'):
        admin_id = request.COOKIES['admin_id']
        print(f"cookie id is -> {admin_id}")
        opass = request.POST['old'] # Getting values from form
        npass = request.POST['new']
        cpass = request.POST['confirm']
        # Fetching Old Password from DB
        cp_query = "select * from tbl_admin where admin_id = %s"
        db_data = db_manager.fetch_one(cp_query, (admin_id,))
        print(f"changepassword-data---------->{db_data}")
        if db_data is not None:
            if len(db_data) > 0:
                oldpassword_db = db_data[3]
                # Comparing Old Password with DB's Old Password
                if opass == oldpassword_db:
                    # Comparing New and Confirm Password
                    if npass != cpass:
                        messages.warning(request, 'New and Confirm Password did not matched !')
                        return render(request, 'admin/changepassword.html')
                    else:
                        updateP_query = "UPDATE tbl_admin SET admin_password = %s WHERE admin_id = %s"
                        db_manager.execute_query(updateP_query, (npass,admin_id))
                        messages.success(request, 'Password Changed Successfully !')
                        return render(request, 'admin/changepassword.html')
                else:
                    messages.warning(request, 'Old Password did not matched !')
                    return render(request, 'admin/changepassword.html')
            else:
                redirect(request, login)
        else:
            redirect(request, login)
    else:
        return redirect(login)  

def forgot(request):
    return render(request,'admin/forgot.html')

def forgotprocess(request):

    f1 = request.POST['email']
    # cur.execute("SELECT * FROM tbl_admin WHERE admin_email = '{}' ".format(f1))
    fp_query = "SELECT * FROM tbl_admin WHERE admin_email = %s"
    # db_admin = cur.fetchone()
    db_admin = db_manager.fetch_one(fp_query, (f1,))
    print(f"forgot password email --->{db_admin}")
    admin_email = db_admin[2]
    # Checking if Email is registered or not
    if f1 == admin_email:
        subject = "Forgot Password"
        admin_name = db_admin[1]
        admin_password = db_admin[3]
        msg = "Hello, " + admin_name + "\nWe have got your request for forgot password \n" + "Your current password is : " + admin_password + "\n Kindly change it for security purpose" + "\n\nThanks & Regards" + "\nTeam - BuildWizard"
        sender = settings.EMAIL_HOST_USER 
        receiver = [request.POST['email']]
        send_mail(subject,msg,sender,receiver)
        messages.success(request," Mail sent, check inbox ")
        return redirect(forgot)
    else:
        messages.error(request, "Email does not exist !")
        return redirect(forgot)


# Manage Product 
def insertproduct(request):
    # cur.execute("SELECT * FROM tbl_category ")
    c_query = "SELECT * FROM tbl_category"

    # cdata = cur.fetchall()
    cdata = db_manager.fetch_all(c_query)

    # cur.execute("SELECT * FROM tbl_brand ")
    b_query = "SELECT * FROM tbl_brand "
    # bdata = cur.fetchall()
    bdata = db_manager.fetch_all(b_query)
    
    return render(request,'admin/insertproduct.html',{'cdata': cdata,'bdata': bdata})

def productimage(request):
    # cur.execute("SELECT * FROM tbl_product ")
    pi_query = "SELECT * FROM tbl_product"
    # pdata = cur.fetchall()
    pdata = db_manager.fetch_all(pi_query)

    return render(request,'admin/insertproductimage.html', {'pdata': pdata})

def productimageprocess(request):
    if request.method == 'POST':
        pn = request.POST['product']
        images = request.FILES.getlist('images')
        print(f"Product ID: {pn}, Images: {images}")

        fs = FileSystemStorage()
        
        for order, img in enumerate(images, start=1):  # Start order from 1
            try:
                myfileupload = fs.save(img.name, img)
                uploaded_file_url = fs.url(myfileupload)

                if uploaded_file_url is None:
                    print(f"Failed to get uploaded file URL for image: {img.name}")
                    messages.error(request, f"Failed to get URL for {img.name}.")
                    continue

                now = datetime.now()
                formatted_datetime = now.strftime('%Y-%m-%d %H:%M:%S')

                print(f"Inserting into DB: Product ID: {pn}, Image Path: {uploaded_file_url}, Image Name: {myfileupload}, Image Order: {order}")
                
                PIP_query = "INSERT INTO tbl_productimages (product_id, image_name, image_order, created_at) VALUES (%s, %s, %s, %s)"
                db_manager.execute_query(PIP_query, (pn, myfileupload, order, formatted_datetime))  # Include order in the query

            except Exception as e:
                print(f"Error uploading {img.name}: {str(e)}")
                messages.error(request, f"Failed to upload image {img.name}. Error: {str(e)}")
                continue

        messages.success(request, 'Images added successfully!')
        
    return redirect(productimage)

def get_category_id(category_name):
    query = "SELECT category_id FROM tbl_category WHERE category_name = %s"
    result = db_manager.fetch_one(query, [category_name])
    return result[0] if result else None

def get_brand_id(brand_name):
    query = "SELECT brand_id FROM tbl_brand WHERE brand_name = %s"
    result = db_manager.fetch_one(query, [brand_name])
    return result[0] if result else None

def productprocess(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:  # Check if the request contains an uploaded file
            excel_file = request.FILES['excel_file']

            # Process Excel file
            try:
                # Read the Excel file
                df = pd.read_excel(excel_file)

                # Validate the required columns in the Excel file
                required_columns = ['product_name', 'product_details', 'product_price', 'category_name', 'brand_name']
                if not all(column in df.columns for column in required_columns):
                    messages.info(request, f'Invalid Excel file format. Required columns: {", ".join(required_columns)}', extra_tags="multiple_product")
                    return redirect(insertproduct)

                # Insert data into the database
                PP_query = """
                    INSERT INTO tbl_product (product_name, product_details, product_price, category_id, brand_id) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                for _, row in df.iterrows():
                    category_id = get_category_id(row['category_name'])
                    brand_id = get_brand_id(row['brand_name'])
                    
                    # Construct product-specific messages
                    product_name = row['product_name']
                    if category_id is None and brand_id is None:
                        messages.warning(request, f'Product "{product_name}" has an invalid category and brand.', extra_tags="multiple_product")
                        continue
                    elif category_id is None:
                        messages.warning(request, f'Product "{product_name}" has an invalid category "{row["category_name"]}".', extra_tags="multiple_product")
                        continue
                    elif brand_id is None:
                        messages.warning(request, f'Product "{product_name}" has an invalid brand "{row["brand_name"]}".', extra_tags="multiple_product")
                        continue
                    
                    db_manager.execute_query(PP_query, (
                        product_name,
                        row['product_details'],
                        row['product_price'],
                        category_id,
                        brand_id
                    ))

                messages.success(request, 'Products uploaded successfully from Excel file!', extra_tags="multiple_product")
            except Exception as e:
                messages.error(request, f'Error processing Excel file: {str(e)}', extra_tags="multiple_product")
            return redirect(insertproduct)

        else:  # Process single product addition from the form
            p1 = request.POST['productname']
            p2 = request.POST['description']
            p3 = request.POST['price']
            p4 = request.POST['category']
            p5 = request.POST['brand']

            # Prepare the SQL query using parameterized query to prevent SQL injection
            PP_query = """
                INSERT INTO tbl_product (product_name, product_details, product_price, category_id, brand_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                db_manager.execute_query(PP_query, (p1, p2, p3, p4, p5))
                messages.success(request, 'Product added successfully!', extra_tags="single_product")
            except Exception as e:
                messages.error(request, f'Error adding product: {str(e)}', extra_tags="single_product")
            return redirect(insertproduct)
    else:
        messages.error(request, 'Invalid request method.')
        return redirect(insertproduct)
    
def displayproduct(request):

    DP_query = ''' 
SELECT
    `tbl_product`.`product_id`
    , `tbl_product`.`product_name`
    , `tbl_product`.`product_details`
    , `tbl_product`.`product_price`
    , `tbl_category`.`category_name`
    , `tbl_brand`.`brand_name`
    , IFNULL(`tbl_productimages`.`image_name`, '') AS image_name

FROM
    `tbl_category`
    INNER JOIN `tbl_product` 
        ON (`tbl_category`.`category_id` = `tbl_product`.`category_id`)
    INNER JOIN `tbl_brand` 
        ON (`tbl_brand`.`brand_id` = `tbl_product`.`brand_id`)
    LEFT JOIN `tbl_productimages` 
        ON (`tbl_productimages`.`product_id` = `tbl_product`.`product_id` AND `tbl_productimages`.`image_order` = 1)
ORDER BY `tbl_product`.`product_id` ASC;
'''
    # data = cur.fetchall()
    data = db_manager.fetch_all(DP_query)
    return render(request,'admin/displayproduct.html',{'mydata': data})

def deleteproduct(request,id):
    print ("Delete item is [ID]---->", id)
    # cur.execute("DELETE FROM tbl_product WHERE product_id = {}".format(id))
    DP_query = "DELETE FROM tbl_product WHERE product_id = %s"
    # conn.commit()
    db_manager.execute_query(DP_query, (id,))
    messages.success(request, 'Product deleted successfully !')
    return redirect(displayproduct)

def editproduct(request,id):

    select_category_q1 = "SELECT * FROM tbl_category"
    cdata = db_manager.fetch_all(select_category_q1)

    select_brand_q2 = "SELECT * FROM tbl_brand"
    bdata = db_manager.fetch_all(select_brand_q2)
    
    print ("Edit item is ",id)
    edit_query = "SELECT * FROM tbl_product WHERE product_id = %s"
    data = db_manager.fetch_one(edit_query, (id,))
    return render(request, 'admin/editproduct.html', {'mydata': data,'cdata': cdata,'bdata': bdata})

def updateproduct(request):
    if request.method == 'POST':
        print(request.POST)
        
        u1 = request.POST['index']
        u2 = request.POST['productname']
        u3 = request.POST['description']
        u4 = request.POST['price']
        u5 = request.POST['category']
        u6 = request.POST['brand']
        u7 = request.FILES['image']
        fs = FileSystemStorage()
        myfileupload = fs.save(u7.name, u7)
        uploaded_file_url = fs.url(myfileupload)
        print ("URL is :  " + uploaded_file_url)

        upd_query = "UPDATE tbl_product SET product_name = %s, product_details = %s, product_price = %s, category_id = %s, brand_id = %s, product_image = %s WHERE product_id = %s"
        db_manager.execute_query(upd_query, (u2,u3,u4,u5,u6,myfileupload,u1))

        messages.success(request, 'Product updated successfully !')
        return redirect(displayproduct)
    else:
        return redirect(displayproduct)

# Brand
def insertbrand(request):
    return render(request,'admin/insertbrand.html')

def brandprocess(request):

    b1 = request.POST['brandname']

    addbrand_query = "INSERT INTO tbl_brand (brand_name) VALUES (%s)"
    db_manager.execute_query(addbrand_query, (b1,))
    messages.success(request, 'Brand added successfully !')
    return redirect(insertbrand)

def displaybrand(request):
    displaybrand_query = "SELECT * FROM tbl_brand "
    data = db_manager.fetch_all(displaybrand_query)
    return render(request,'admin/displaybrand.html',{'mydata': data})

def deletebrand(request,id):
    print ("Delete item is [id]---->", id)
    deletebrand_query = "DELETE FROM tbl_brand WHERE brand_id = %s"
    db_manager.execute_query(deletebrand_query, (id,))
    messages.success(request, 'Brand deleted successfully !')
    return redirect(displaybrand)

def editbrand(request,id):
    print ("Edit item is ",id)
    editbrand_query = "SELECT * FROM tbl_brand WHERE brand_id = %s"
    data = db_manager.fetch_one(editbrand_query, (id,))
    return render(request, 'admin/editbrand.html', {'mydata': data})

def updatebrand(request):
    if request.method == 'POST':
        print(request.POST)
        
        u1 = request.POST['index']
        u2 = request.POST['brandname']
        
        updatebrand_query = "UPDATE tbl_brand SET brand_name =%s WHERE brand_id =%s"
        db_manager.execute_query(updatebrand_query, (u2,u1))
        messages.success(request, 'Brand updated successfully !')
        return redirect(displaybrand)
    else:
        return redirect(displaybrand)

# Categories
def insertcategory(request):
    return render(request,'admin/insertcategory.html')

def categoryprocess(request):

    c1 = request.POST['categoryname']

    addcategory_query = "INSERT INTO tbl_category (category_name) VALUES (%s)"
    db_manager.execute_query(addcategory_query, (c1,))
    messages.success(request, 'Category added successfully !')
    return redirect(insertcategory)

def displaycategory(request):
    displaycategory_query = "SELECT * FROM tbl_category "
    data = db_manager.fetch_all(displaycategory_query)
    return render(request,'admin/displaycategory.html',{'mydata': data})

def deletecategory(request,id):
    print ("Delete item is [id] ------>", id)
    deletecategory_query = "DELETE FROM tbl_category WHERE category_id = %s"
    db_manager.execute_query(deletecategory_query, (id,))
    messages.success(request, 'Category deleted successfully !')
    return redirect(displaycategory)

def editcategory(request,id):
    print ("Edit item is ",id)
    editcategory_query = "SELECT * FROM tbl_category WHERE category_id = %s"
    data = db_manager.fetch_one(editcategory_query, (id,))
    return render(request, 'admin/editcategory.html', {'mydata': data})

def updatecategory(request):
    if request.method == 'POST':
        print(request.POST)
        
        u1 = request.POST['index']
        u2 = request.POST['categoryname']
        
        deletecategory_query = "UPDATE tbl_category SET category_name =%s WHERE category_id =%s"
        db_manager.execute_query(deletecategory_query, (u2,u1))
        messages.success(request, 'Category updated successfully !')
        return redirect(displaycategory)
    else:
        return redirect(displaycategory)

# Orders SECTION
def displayorders(request):
    displayorders_query = "SELECT * FROM tbl_ordermaster"
    data = db_manager.fetch_all(displayorders_query)
    print (list(data))
    return render(request,'admin/displayorders.html',{'mydata': data})

def editorders(request,id):
    editorders_query = "SELECT * FROM tbl_ordermaster WHERE order_id = %s"
    data = db_manager.fetch_one(editorders_query, (id,))
    return render(request, 'admin/editorders.html', {'mydata': data})

def updatestatus(request):
    if request.method == 'POST':
        o1 = request.POST['index']
        o2 = request.POST['status']

        editorders_query = "UPDATE tbl_ordermaster SET order_status =%s WHERE order_id =%s"
        db_manager.execute_query(editorders_query, (o2,o1))
        messages.success(request, 'Order Status Changed successfully !')
        return redirect(displayorders)
    else:
        return redirect(displayorders)

# Order details SECTION
def displayorderdetails(request):

    displayorderdetails_query = '''SELECT
    `tbl_orderdetails`.`details_id`
    , `tbl_orderdetails`.`order_id`
    , `tbl_product`.`product_name`
    , `tbl_orderdetails`.`quantity`
    , `tbl_orderdetails`.`price`
FROM
    `buildwizard`.`tbl_product`
    INNER JOIN `buildwizard`.`tbl_orderdetails` 
        ON (`tbl_product`.`product_id` = `tbl_orderdetails`.`product_id`);'''
    data = db_manager.fetch_all(displayorderdetails_query)
    print (list(data))
    return render(request,'admin/displayorderdetails.html',{'mydata': data})

# Community Forums SECTION
def forums(request):
    displayforums_query = "SELECT * FROM tbl_forums"
    data = db_manager.fetch_all(displayforums_query)
    return render(request,'admin/displayforums.html',{'mydata':data})

def deleteforums(request,id):
    deleteforums_query = "DELETE FROM tbl_forums WHERE forum_id = %s"
    db_manager.execute_query(deleteforums_query, (id,))
    messages.success(request, 'Forum deleted successfully !')
    return redirect(forums)

# REPORTS SECTION
def reportproduct_category(request):
    reportproduct_category_query = "SELECT * FROM tbl_category"
    data = db_manager.fetch_all(reportproduct_category_query)
    #return list(data)
    print(list(data))
    return render(request,'admin/productreport.html',{'mydata':data})

def reportproduct_category_process(request):
    if request.method == 'POST':
        print(request.POST)
        id = request.POST['txt1']
        reportproduct_category_process_query = "SELECT * FROM tbl_category"
        data = db_manager.fetch_all(reportproduct_category_process_query)

        reportproduct_category_query2 = '''SELECT
    `tbl_product`.`product_id`
    , `tbl_product`.`product_name`
    , `tbl_product`.`product_details`
    , `tbl_product`.`product_price`
    , `tbl_category`.`category_name`
    , `tbl_brand`.`brand_name`
    , `tbl_productimages`.`image_name`

FROM
    `tbl_category`
    INNER JOIN `tbl_product` 
        ON (`tbl_category`.`category_id` = `tbl_product`.`category_id`)
    INNER JOIN `tbl_brand` 
        ON (`tbl_brand`.`brand_id` = `tbl_product`.`brand_id`)
    INNER JOIN `tbl_productimages`
        ON (`tbl_productimages`.`product_id` = `tbl_product`.`product_id`) 
WHERE
    `tbl_productimages`.`image_order` = 1
    AND 
    `tbl_category`.`category_id` = %s '''

        data1 = db_manager.fetch_all(reportproduct_category_query2, (id,))
        return render(request,'admin/productreport.html',{'mydata':data,'mydata1':data1})
    else:
        return redirect(reportproduct_category)

def reportproduct_brand(request):
    reportproduct_brand_query = "SELECT * FROM tbl_brand"
    data = db_manager.fetch_all(reportproduct_brand_query)
    #return list(data)
    print(list(data))
    return render(request,'admin/productreport2.html',{'mydata':data})

def reportproduct_brand_process(request):
    if request.method == 'POST':
        print(request.POST)
        id = request.POST['txt1']
        reportproduct_brand_process_query = "SELECT * FROM tbl_brand"
        data = db_manager.fetch_all(reportproduct_brand_process_query)
        reportproductb2_query2 = '''SELECT
    `tbl_product`.`product_id`
    , `tbl_product`.`product_name`
    , `tbl_product`.`product_details`
    , `tbl_product`.`product_price`
    , `tbl_category`.`category_name`
    , `tbl_brand`.`brand_name`
    , `tbl_productimages`.`image_name`
FROM
    `tbl_category`
    INNER JOIN `tbl_product` 
        ON (`tbl_category`.`category_id` = `tbl_product`.`category_id`)
    INNER JOIN `tbl_brand` 
        ON (`tbl_brand`.`brand_id` = `tbl_product`.`brand_id`)
    INNER JOIN `tbl_productimages`
        ON (`tbl_productimages`.`product_id` = `tbl_product`.`product_id`)  
WHERE 
    `tbl_productimages`.`image_order` = 1
    AND 
    `tbl_brand`.`brand_id` = %s '''

        data1 = db_manager.fetch_all(reportproductb2_query2, (id,))
        return render(request,'admin/productreport2.html',{'mydata':data,'mydata1':data1})
    else:
        return redirect(reportproduct_brand)
    
def reportorder_datewise(request):
    reportorder_datewise_query = "SELECT * FROM tbl_ordermaster"
    data = db_manager.fetch_all(reportorder_datewise_query)
    #return list(data)
    print(list(data))
    return render(request,'admin/orderreport.html',{'mydata':data})

def reportorder_datewise_process(request):
    if request.method == 'POST':
        print(request.POST)
        sd = request.POST['txt1']
        ed = request.POST['txt2']
        reportorder_datewise_query = "SELECT * FROM tbl_ordermaster"
        data = db_manager.fetch_all(reportorder_datewise_query)
        reportorder2_query2 = '''SELECT
    `tbl_ordermaster`.`order_id`
    , `tbl_ordermaster`.`order_date`
    , `tbl_ordermaster`.`order_status`
    , `tbl_user`.`user_name`
    , `tbl_ordermaster`.`mode_of_payment`
    , `tbl_ordermaster`.`shipping_name`
    , `tbl_ordermaster`.`shipping_mobile`
    , `tbl_ordermaster`.`shipping_address`
FROM
    `buildwizard`.`tbl_user`
    INNER JOIN `buildwizard`.`tbl_ordermaster` 
        ON (`tbl_user`.`user_id` = `tbl_ordermaster`.`user_id`) 
        WHERE order_date between %s and %s '''

        data1 = db_manager.fetch_all(reportorder2_query2, (sd,ed))
        return render(request,'admin/orderreport.html',{'mydata':data,'mydata1':data1})
    else:
        return redirect(reportorder_datewise)
    
def reportorder_userwise(request):
    reportorder_userwise_query = "SELECT * FROM tbl_user"
    data = db_manager.fetch_all(reportorder_userwise_query)
    #return list(data)
    print(list(data))
    return render(request,'admin/orderreport2.html',{'mydata':data})

def reportorder_userwise_process(request):
    if request.method == 'POST':
        print(request.POST)
        uname = request.POST['txt1']
        reportorder_datewise_process_query = "SELECT * FROM tbl_user"
        data = db_manager.fetch_all(reportorder_datewise_process_query)
        reportorder_userwise_query = '''SELECT
    `tbl_ordermaster`.`order_id`
    , `tbl_ordermaster`.`order_date`
    , `tbl_ordermaster`.`order_status`
    , `tbl_user`.`user_name`
    , `tbl_ordermaster`.`mode_of_payment`
    , `tbl_ordermaster`.`shipping_name`
    , `tbl_ordermaster`.`shipping_mobile`
    , `tbl_ordermaster`.`shipping_address`
FROM
    `buildwizard`.`tbl_user`
    INNER JOIN `buildwizard`.`tbl_ordermaster` 
        ON (`tbl_user`.`user_id` = `tbl_ordermaster`.`user_id`) WHERE `tbl_user`.`user_id` =  %s '''

        data1 = db_manager.fetch_all(reportorder_userwise_query, (uname,))
        return render(request,'admin/orderreport2.html',{'mydata':data,'mydata1':data1})
    else:
        return redirect(reportorder_userwise)

    