import pymysql

conn = pymysql.connect(
    host='mysql-35a2efd8-aleronpeterson-6630.l.aivencloud.com',
    user='avnadmin',
    password='AVNS_dzrOiUs7-uI2sv17LMW',
    database='defaultdb',
    port=19275,
    ssl={'ca': r'F:\Flask_Projects\E-library\certs\ca.pem'}
)

with conn.cursor() as cursor:
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    print("Connected to database:", result[0])

conn.close()
