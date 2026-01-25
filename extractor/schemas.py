"""
Data Schemas

Pydantic models for structured document data.
Used for validation and serialization of extracted data.
"""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """A single line item from an invoice."""
    description: str
    quantity: float = 1.0
    unit_price: float
    amount: float


class InvoiceData(BaseModel):
    """Structured data from an invoice document."""
    
    invoice_number: Optional[str] = None
    date: Optional[date] = None
    due_date: Optional[date] = None
    
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    
    currency: str = "USD"
    
    line_items: List[LineItem] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice_number": "INV-2024-001",
                "date": "2024-01-15",
                "vendor_name": "ABC Company",
                "total_amount": 1250.00,
                "currency": "USD"
            }
        }


class ReceiptItem(BaseModel):
    """A single item from a receipt."""
    name: str
    quantity: float = 1.0
    price: float


class ReceiptData(BaseModel):
    """Structured data from a receipt document."""
    
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    
    date: Optional[date] = None
    time: Optional[str] = None
    
    items: List[ReceiptItem] = Field(default_factory=list)
    
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    
    payment_method: Optional[str] = None
    currency: str = "USD"


class Allowance(BaseModel):
    """An allowance component in a salary slip."""
    name: str
    amount: float


class Deduction(BaseModel):
    """A deduction component in a salary slip."""
    name: str
    amount: float


class SalarySlipData(BaseModel):
    """Structured data from a salary slip document."""
    
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    company_name: Optional[str] = None
    
    pay_period: Optional[str] = None
    pay_date: Optional[date] = None
    
    basic_salary: Optional[float] = None
    
    allowances: List[Allowance] = Field(default_factory=list)
    deductions: List[Deduction] = Field(default_factory=list)
    
    gross_salary: Optional[float] = None
    net_salary: Optional[float] = None
    
    currency: str = "USD"
