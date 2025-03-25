import pymongo
from datetime import datetime, timedelta

# MongoDB connection
MONGO_URI = "mongodb+srv://joshuailangovansamuel:i9KNhtkqhUibQEer@cluster0.pbvcd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client['diabetes']
patients_collection = db['patients']

# Clear existing records
patients_collection.delete_many({})
print("Cleared existing records in the patients collection.")

# Detailed patient data (daily monitoring for a week)
patients = [
    {
        "name": "Sofia Alvarez",
        "age": 48,
        "gender": "Female",
        "contact": "sofia.alvarez@example.com",
        "diagnosis_date": "2023-03-10",
        "retinopathy_stage": "Mild",
        "daily_monitoring": [
            {"date": (datetime.now() - timedelta(days=6)).isoformat(), "blood_sugar": 130, "activity": "30 min walk", "meal": "Oatmeal, fruit"},
            {"date": (datetime.now() - timedelta(days=5)).isoformat(), "blood_sugar": 135, "activity": "Yoga", "meal": "Grilled chicken, veggies"},
            {"date": (datetime.now() - timedelta(days=4)).isoformat(), "blood_sugar": 128, "activity": "Rest", "meal": "Rice, beans"},
            {"date": (datetime.now() - timedelta(days=3)).isoformat(), "blood_sugar": 140, "activity": "20 min jog", "meal": "Pasta, salad"},
            {"date": (datetime.now() - timedelta(days=2)).isoformat(), "blood_sugar": 132, "activity": "Gym", "meal": "Fish, quinoa"},
            {"date": (datetime.now() - timedelta(days=1)).isoformat(), "blood_sugar": 137, "activity": "Rest", "meal": "Soup, bread"},
            {"date": datetime.now().isoformat(), "blood_sugar": 129, "activity": "30 min walk", "meal": "Eggs, toast"}
        ],
        "medication_adherence": [True, True, False, True, True, True, False],
        "recommendations": {
            "medication": "Metformin daily",
            "lifestyle": "Maintain exercise routine",
            "next_checkup": "2024-03-10"
        }
    },
    {
        "name": "Liam Chen",
        "age": 55,
        "gender": "Male",
        "contact": "liam.chen@example.com",
        "diagnosis_date": "2022-08-15",
        "retinopathy_stage": "Moderate",
        "daily_monitoring": [
            {"date": (datetime.now() - timedelta(days=6)).isoformat(), "blood_sugar": 150, "activity": "Cycling", "meal": "Porridge"},
            {"date": (datetime.now() - timedelta(days=5)).isoformat(), "blood_sugar": 165, "activity": "Rest", "meal": "Burger, fries"},
            {"date": (datetime.now() - timedelta(days=4)).isoformat(), "blood_sugar": 155, "activity": "Swimming", "meal": "Salmon, rice"},
            {"date": (datetime.now() - timedelta(days=3)).isoformat(), "blood_sugar": 160, "activity": "Rest", "meal": "Pizza"},
            {"date": (datetime.now() - timedelta(days=2)).isoformat(), "blood_sugar": 170, "activity": "20 min walk", "meal": "Chicken, veggies"},
            {"date": (datetime.now() - timedelta(days=1)).isoformat(), "blood_sugar": 158, "activity": "Gym", "meal": "Noodles"},
            {"date": datetime.now().isoformat(), "blood_sugar": 162, "activity": "Rest", "meal": "Steak, potatoes"}
        ],
        "medication_adherence": [True, False, True, False, True, False, True],
        "recommendations": {
            "medication": "Insulin twice daily",
            "lifestyle": "Reduce carb intake",
            "next_checkup": "2023-12-15"
        }
    },
    {
        "name": "Aisha Khan",
        "age": 62,
        "gender": "Female",
        "contact": "aisha.khan@example.com",
        "diagnosis_date": "2021-05-20",
        "retinopathy_stage": "Severe",
        "daily_monitoring": [
            {"date": (datetime.now() - timedelta(days=6)).isoformat(), "blood_sugar": 190, "activity": "Rest", "meal": "Bread, butter"},
            {"date": (datetime.now() - timedelta(days=5)).isoformat(), "blood_sugar": 200, "activity": "10 min walk", "meal": "Rice, curry"},
            {"date": (datetime.now() - timedelta(days=4)).isoformat(), "blood_sugar": 195, "activity": "Rest", "meal": "Pasta"},
            {"date": (datetime.now() - timedelta(days=3)).isoformat(), "blood_sugar": 210, "activity": "Rest", "meal": "Cake, tea"},
            {"date": (datetime.now() - timedelta(days=2)).isoformat(), "blood_sugar": 205, "activity": "15 min walk", "meal": "Fish, salad"},
            {"date": (datetime.now() - timedelta(days=1)).isoformat(), "blood_sugar": 198, "activity": "Rest", "meal": "Soup"},
            {"date": datetime.now().isoformat(), "blood_sugar": 215, "activity": "Rest", "meal": "Chicken, rice"}
        ],
        "medication_adherence": [False, True, False, False, True, False, False],
        "recommendations": {
            "medication": "Insulin + laser therapy",
            "lifestyle": "Strict diet control",
            "next_checkup": "2023-11-20"
        }
    }
]

# Insert patients into MongoDB
patients_collection.insert_many(patients)
print(f"Added {len(patients)} patients with detailed monitoring data.")

# Close connection
client.close()