from dataclasses import dataclass

@dataclass
class product:
    id: int
    title: str
    price: int
    shop: str
    
@dataclass
class alert:
    search_text: str
    alert_price: int