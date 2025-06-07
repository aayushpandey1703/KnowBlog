import pymysql
import argparse
class Add:
    def add(self,read=None):
        conn = pymysql.connect(
            host='mysql-35a2efd8-aleronpeterson-6630.l.aivencloud.com',
            user='avnadmin',
            password='AVNS_dzrOiUs7-uI2sv17LMW',
            database='defaultdb',
            port=19275,
            ssl={'ca': r'F:\Flask_Projects\Blog\certs\ca.pem'}
        )

        if args.read:
            tablename=args.read

        if args.read == None:
            with conn.cursor() as cursor:
                print("Connected to database")
                cursor.execute(f"CREATE TABLE Blog (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), content TEXT, author VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                conn.commit()
                cursor.close()

        if args.read:
            with conn.cursor() as cursor:
                print("Connected to database")
                cursor.execute(f"select * from {tablename}")
                result=cursor.fetchall()
                print(result)
                cursor.close()

        conn.close()

if __name__=="__main__":
    print("De")
    parser=argparse.ArgumentParser()
    parser.add_argument("--read",nargs='?')
    args=parser.parse_args()
    print(args)
    add=Add()
    add.add(read=args.read)
    
# python testdb.py --read "Blog"
