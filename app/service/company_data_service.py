from app.dto.company_scraped_data_dto import CompanyDTO, ProductDTO

async def fetch_company_data(company_name: str) -> CompanyDTO:
    """
    Simulate fetching company data based on the company name.
    """
    mock_data = {
        "Smith Construction Ltd.": CompanyDTO(
            id=1,
            name="Smith Construction Ltd.",
            industry="Construction",
            location="Toronto, Canada",
            type="Private",
            size="150 employees",
            annual_revenue=25000000.0,
            market_cap=0.0,
            key_products=[
                ProductDTO(name="Residential Housing", description="Affordable residential housing projects"),
                ProductDTO(name="Office Buildings", description="Mid-size office buildings in urban centers")
            ],
            sustainability_goals="Implement energy-efficient building designs by 2026.",
            social_goals="Offer internships for local students in the trades.",
            governance="Adhere to local and federal building standards with transparency."
        ),
        "Maple Foods Inc.": CompanyDTO(
            id=2,
            name="Maple Foods Inc.",
            industry="Food Processing",
            location="Montreal, Canada",
            type="Public",
            size="500 employees",
            annual_revenue=75000000.0,
            market_cap=120000000.0,
            key_products=[
                ProductDTO(name="Canned Soups", description="Wide range of canned soups for everyday meals"),
                ProductDTO(name="Frozen Vegetables", description="Packaged frozen vegetables for retail and wholesale"),
                ProductDTO(name="Ready-to-Eat Meals", description="Microwaveable meals for busy households")
            ],
            sustainability_goals="Reduce packaging waste by 30% by 2028.",
            social_goals="Partner with food banks to donate surplus production.",
            governance="Quarterly board reviews on food safety and compliance."
        ),
        "Urban Outfitters Co.": CompanyDTO(
            id=3,
            name="Urban Outfitters Co.",
            industry="Clothing Retail",
            location="Calgary, Canada",
            type="Private",
            size="100 employees",
            annual_revenue=10000000.0,
            market_cap=0.0,
            key_products=[
                ProductDTO(name="Casual Wear", description="Trendy and affordable casual wear for men and women"),
                ProductDTO(name="Outerwear", description="Seasonal jackets and coats"),
                ProductDTO(name="Accessories", description="Fashionable accessories including scarves and hats")
            ],
            sustainability_goals="Introduce a clothing recycling program by 2025.",
            social_goals="Support local charities with annual fundraising events.",
            governance="Transparent labor practices with supplier accountability."
        ),
        "Northern Logistics Corp.": CompanyDTO(
            id=4,
            name="Northern Logistics Corp.",
            industry="Logistics and Warehousing",
            location="Edmonton, Canada",
            type="Public",
            size="800 employees",
            annual_revenue=150000000.0,
            market_cap=250000000.0,
            key_products=[
                ProductDTO(name="Freight Services", description="Nationwide freight transportation services"),
                ProductDTO(name="Warehousing Solutions", description="Temperature-controlled and standard warehousing options"),
                ProductDTO(name="Supply Chain Consulting", description="Optimized supply chain solutions for businesses")
            ],
            sustainability_goals="Transition 20% of the fleet to electric vehicles by 2030.",
            social_goals="Support employment opportunities in underserved regions.",
            governance="Annual compliance reviews for fleet safety and emissions."
        ),
        "Horizon Hospitality Group": CompanyDTO(
            id=5,
            name="Horizon Hospitality Group",
            industry="Hospitality",
            location="Vancouver, Canada",
            type="Private",
            size="250 employees",
            annual_revenue=35000000.0,
            market_cap=0.0,
            key_products=[
                ProductDTO(name="Luxury Hotels", description="Boutique hotels with premium amenities"),
                ProductDTO(name="Conference Services", description="Facilities and services for corporate events"),
                ProductDTO(name="Fine Dining Restaurants", description="Award-winning restaurants in major cities")
            ],
            sustainability_goals="Adopt water-saving technologies in all properties by 2027.",
            social_goals="Offer scholarships to hospitality students from disadvantaged backgrounds.",
            governance="Independent audits on food safety and guest satisfaction."
        ),
    }

    # Return data or raise exception if company is not found
    if company_name not in mock_data:
        raise ValueError(f"Company data not found for: {company_name}")
    return mock_data[company_name]
