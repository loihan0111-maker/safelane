from fastapi import FastAPI, HTTPException, Query
import requests
from typing import List, Optional

app = FastAPI(title="Safe Lane ELD Integration API")

# Doimiy o'zgarmaslar
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Prefer': 'count=estimated',
    'X-Eld-Request-Id': '16c65a79-5d96-4b0b-b1dc-41b44c1034b3',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIiA6ICJtYW5hZ2VyIiwgImV4cCIgOiAyMDkxOTIyMjM3LCAic3ViIiA6ICJjZGNjZGM1My0yYjEyLTQ4ZDItYTEzZC0yMDU4OTBlZWUyYWUiLCAiaWF0IiA6IDE3NzY1NjIyMzcsICJjb21wYW55X2lkIiA6IG51bGwsICJ2ZXJzaW9uIiA6ICIyLjAiLCAic2Vzc2lvbl9pZCIgOiAiZDhkODk4N2EtNzllMC00M2NkLTg4NWEtZWJlOWI0ODQwMWZkIiwgInVwc3RyZWFtX2hvc3QiIDogImh0dHA6Ly9yZXN0LnNhZmVsYW5lLnN2Yy5jbHVzdGVyLmxvY2FsOjMwMDAifQ.rJfxHIPcUDYrNcc6oxJXwebIJtax-L3aleZbtirOfaA',
    'Connection': 'keep-alive',
    'Referer': 'https://cloud.safelaneeld.com/c/9fcd87d1-00a2-4fbc-8f5c-a967131cf28f/vehicles',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}
BASE_URL = 'https://cloud.safelaneeld.com/rest/vehicles_with_state_view'
# COMPANY_ID = '9fcd87d1-00a2-4fbc-8f5c-a967131cf28f'

@app.get("/vehicles")
def get_vehicles(
    company_id: str = Query(..., description="Safe Lane kompaniya ID raqami"),
    limit: int = 400, 
    offset: int = 0
):
    """
    Tashqi API'dan berilgan company_id ga tegishli transport vositalarini oladi.
    """
    
    # So'rov parametrlarini shakllantirish
    # Company_id endi bevosita foydalanuvchi yuborgan qiymatdan olinadi
    params = {
        'order': 'vehicle_state_updated_at.desc.nullslast',
        'and': f'(company_id.eq.{company_id},and(is_active.eq.true))',
        'offset': offset,
        'limit': limit
    }
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Token muddati tugagan yoki noto'g'ri")
        
        response.raise_for_status()
        data = response.json()
    
        # Ma'lumotlarni filtrlash
        filtered_data = [
            {
                "id": item.get("name"),
                "vin": item.get("vin"),
                "driver": item.get("full_name"),
                "lat": item.get("location_lat"),
                "lon": item.get("location_lon"),
                "odometer": item.get("odometer")*0.621371,
                "engine_hours": item.get("engine_hours")
            }
            for item in data
        ]
        
        return {
            "status": "success",
            "company_id": company_id,
            "count": len(filtered_data),
            "data": filtered_data
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Tizim xatosi: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)