"""
Vision AI Module

Handles communication with OpenAI's Vision API for document analysis.
Includes prompt engineering for accurate data extraction.
"""

import os
import base64
from typing import Optional, Dict, Any
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

from extractor.schemas import InvoiceData, ReceiptData, SalarySlipData


# Load environment variables
load_dotenv()


class VisionAI:
    """
    OpenAI Vision API wrapper for document analysis.
    
    Handles image encoding, prompt construction, and API communication.
    Uses structured prompts to ensure consistent data extraction.
    
    Attributes:
        client: OpenAI client instance
        model: Vision model to use (default: gpt-4-vision-preview)
        max_tokens: Maximum tokens for response
    """
    
    # Extraction prompts for different document types
    PROMPTS = {
        'invoice': """
            Analyze this invoice image and extract the following information in JSON format:
            {
                "invoice_number": "string or null",
                "date": "YYYY-MM-DD format or null",
                "due_date": "YYYY-MM-DD format or null",
                "vendor_name": "string or null",
                "vendor_address": "string or null",
                "customer_name": "string or null",
                "customer_address": "string or null",
                "subtotal": "number or null",
                "tax_amount": "number or null",
                "total_amount": "number or null",
                "currency": "string (e.g., USD, EUR) or null",
                "line_items": [
                    {
                        "description": "string",
                        "quantity": "number",
                        "unit_price": "number",
                        "amount": "number"
                    }
                ]
            }
            
            Important:
            - Extract exact values as shown in the document
            - Use null for fields that are not visible or unclear
            - Amounts should be numbers without currency symbols
            - Return only valid JSON, no explanations
        """,
        
        'receipt': """
            Analyze this receipt image and extract the following information in JSON format:
            {
                "store_name": "string or null",
                "store_address": "string or null",
                "date": "YYYY-MM-DD format or null",
                "time": "HH:MM format or null",
                "items": [
                    {
                        "name": "string",
                        "quantity": "number",
                        "price": "number"
                    }
                ],
                "subtotal": "number or null",
                "tax": "number or null",
                "total": "number or null",
                "payment_method": "string or null",
                "currency": "string or null"
            }
            
            Important:
            - Extract exact values as shown
            - Use null for unclear or missing fields
            - Return only valid JSON
        """,
        
        'salary_slip': """
            Analyze this salary slip/payslip image and extract the following information in JSON format:
            {
                "employee_name": "string or null",
                "employee_id": "string or null",
                "company_name": "string or null",
                "pay_period": "string or null",
                "pay_date": "YYYY-MM-DD format or null",
                "basic_salary": "number or null",
                "allowances": [
                    {
                        "name": "string",
                        "amount": "number"
                    }
                ],
                "deductions": [
                    {
                        "name": "string",
                        "amount": "number"
                    }
                ],
                "gross_salary": "number or null",
                "net_salary": "number or null",
                "currency": "string or null"
            }
            
            Important:
            - Extract exact values as shown
            - Use null for unclear or missing fields
            - Return only valid JSON
        """,
        
        'auto': """
            Analyze this document image. First determine what type of document it is 
            (invoice, receipt, salary slip, or other), then extract all relevant 
            structured data in JSON format.
            
            Include a "document_type" field in your response indicating what type 
            of document this is.
            
            Extract all visible text data in a structured format appropriate for 
            the document type. Return only valid JSON.
        """
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vision AI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            
        Raises:
            ValueError: If no API key is provided or found
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("VISION_MODEL", "gpt-4-vision-preview")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def get_image_media_type(self, image_path: str) -> str:
        """
        Determine the media type of an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Media type string (e.g., 'image/png')
        """
        extension = Path(image_path).suffix.lower()
        
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        
        return media_types.get(extension, 'image/png')
    
    def analyze_document(
        self, 
        image_path: str, 
        document_type: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Analyze a document image and extract structured data.
        
        Args:
            image_path: Path to the document image
            document_type: Type of document (invoice, receipt, salary_slip, auto)
            
        Returns:
            Dictionary containing extracted data
        """
        # Get the appropriate prompt
        prompt = self.PROMPTS.get(document_type, self.PROMPTS['auto'])
        
        # Encode the image
        base64_image = self.encode_image(image_path)
        media_type = self.get_image_media_type(image_path)
        
        # Create the API request
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=self.max_tokens
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Parse JSON from response
        return self._parse_json_response(content)
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON from the API response.
        
        Handles cases where the response might include markdown code blocks
        or additional text around the JSON.
        
        Args:
            content: Raw response content from the API
            
        Returns:
            Parsed dictionary
        """
        import json
        import re
        
        # Try to find JSON in the response
        # First, try to parse the entire content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object in the text
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Return empty dict if parsing fails
        return {"error": "Failed to parse response", "raw_content": content}
