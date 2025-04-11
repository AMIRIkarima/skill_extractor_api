from pymongo import MongoClient

uri = "mongodb+srv://ayamoukil2210:XuQx3XWilrNaVdRB@cluster0.l28hq.mongodb.net/job_finder?retryWrites=true&w=majority"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=50000)
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print("❌ Connection failed:", e)
