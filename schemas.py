"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (kept for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Real estate app schemas

class Listing(BaseModel):
    """
    Real estate property listing
    Collection: "listing"
    """
    title: str = Field(..., description="Short headline for the property")
    address: str = Field(..., description="Property address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State or region")
    price: int = Field(..., ge=0, description="Price in whole currency units")
    beds: int = Field(..., ge=0, description="Number of bedrooms")
    baths: float = Field(..., ge=0, description="Number of bathrooms")
    sqft: int = Field(..., ge=0, description="Square footage")
    image: Optional[str] = Field(None, description="Hero image URL")
    gallery: Optional[List[str]] = Field(default=None, description="Additional image URLs")
    featured: bool = Field(default=False, description="Show as featured on homepage")
    property_type: str = Field(default="House", description="Type of property")

class Inquiry(BaseModel):
    """
    Contact/inquiry for a listing
    Collection: "inquiry"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    message: str = Field(..., min_length=5, max_length=2000, description="Message body")
    property_id: Optional[str] = Field(None, description="Related listing id")
