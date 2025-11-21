import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Models (responses/payloads) ----------
class ListingOut(BaseModel):
    id: Optional[str] = Field(default=None, description="Document id as string")
    title: str
    address: str
    city: str
    state: str
    price: int
    beds: int
    baths: float
    sqft: int
    image: Optional[str] = None
    gallery: Optional[List[str]] = None
    featured: bool = False
    property_type: str = "House"


class InquiryIn(BaseModel):
    name: str
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)
    property_id: Optional[str] = None


# ---------- Demo data fallback if DB unavailable ----------
DEMO_LISTINGS: List[ListingOut] = [
    ListingOut(
        id="demo-1",
        title="Modern Smart Home with Skyline Views",
        address="123 Aurora Ave",
        city="San Francisco",
        state="CA",
        price=1895000,
        beds=4,
        baths=3.5,
        sqft=2560,
        image="https://images.unsplash.com/photo-1507089947368-19c1da9775ae?w=1600",
        gallery=None,
        featured=True,
        property_type="House",
    ),
    ListingOut(
        id="demo-2",
        title="Sleek Downtown Loft",
        address="77 Horizon St Apt 12B",
        city="New York",
        state="NY",
        price=1299000,
        beds=2,
        baths=2,
        sqft=1180,
        image="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=1600",
        featured=True,
        property_type="Condo",
    ),
    ListingOut(
        id="demo-3",
        title="Sunlit Suburban Retreat",
        address="940 Evergreen Dr",
        city="Austin",
        state="TX",
        price=739000,
        beds=3,
        baths=2,
        sqft=1920,
        image="https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=1600",
        featured=False,
        property_type="House",
    ),
]


# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables explicitly
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.get("/api/listings", response_model=List[ListingOut])
def get_listings(featured: Optional[bool] = None, limit: Optional[int] = None):
    """Return listings from DB if available, otherwise demo data."""
    try:
        from database import db
        if db is not None:
            query = {}
            if featured is not None:
                query["featured"] = featured
            cursor = db["listing"].find(query).sort("created_at", -1)
            if limit:
                cursor = cursor.limit(limit)
            items: List[ListingOut] = []
            for doc in cursor:
                doc_id = str(doc.get("_id"))
                doc["id"] = doc_id
                doc.pop("_id", None)
                items.append(ListingOut(**doc))
            if items:
                return items
    except Exception:
        # Fall back to demo if any DB error
        pass

    data = DEMO_LISTINGS
    if featured is not None:
        data = [d for d in data if d.featured == featured]
    if limit is not None:
        data = data[:limit]
    return data


@app.post("/api/inquiries")
def create_inquiry(payload: InquiryIn):
    """Store inquiry in DB if available; otherwise accept and return ack."""
    try:
        from database import create_document
        doc_id = create_document("inquiry", payload.model_dump())
        return {"status": "ok", "id": doc_id}
    except Exception:
        # Accept but not persisted
        return {"status": "ok", "id": "demo"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
