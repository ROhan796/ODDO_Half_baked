"""Data pools for comprehensive database seeding."""

NAMES_POOL = [
    "Aarav Sharma", "Aditi Rao", "Amitav Ghosh", "Ananya Pandey", "Anish Varma",
    "Ankita Roy", "Arnav Malhotra", "Bhavna Patel", "Chetan Bhagat", "Deepika Padukone",
    "Devansh Mehta", "Divya Agarwal", "Gaurav Sen", "Harshvardhan Kapoor", "Isha Ambani",
    "Jatin Merchant", "Kabir Bedi", "Kavya Nair", "Karan Johar", "Kriti Sanon",
    "Madhavan Pillai", "Manish Malhotra", "Meera Rajput", "Nikhil Kamath", "Nisha Guragain",
    "Pooja Hegde", "Pranav Reddy", "Radhika Merchant", "Rahul Dravid", "Rohan Manna",
    "Rishabh Pant", "Riya Sen", "Rohan Joshi", "Sameer Verma", "Siddharth Malhotra",
    "Sneha Ullal", "Srikant Tiwari", "Subhash Ghai", "Sunil Chhetri", "Tanya Shroff",
    "Tarun Tahiliani", "Utkarsh Ambudkar", "Varun Dhawan", "Vidya Balan", "Vikramaditya Motwane",
    "Yash Dasgupta", "Yuvraj Singh", "Zoya Akhtar", "Kunal Shah", "Nandan Nilekani"
]

CITIES_POOL = [
    {"city": "Bangalore", "state": "Karnataka", "pincode": "560001", "address": "100ft Road, Indiranagar"},
    {"city": "Mumbai", "state": "Maharashtra", "pincode": "400050", "address": "Bandra Kurla Complex, Bandra East"},
    {"city": "Delhi", "state": "Delhi", "pincode": "110001", "address": "Connaught Place, Inner Circle"},
    {"city": "Hyderabad", "state": "Telangana", "pincode": "500081", "address": "HITEC City, Madhapur"},
    {"city": "Chennai", "state": "Tamil Nadu", "pincode": "600034", "address": "Nungambakkam High Road"},
    {"city": "Pune", "state": "Maharashtra", "pincode": "411006", "address": "Koregaon Park, North Main Road"},
    {"city": "Kolkata", "state": "West Bengal", "pincode": "700091", "address": "Salt Lake Sector V"},
    {"city": "Ahmedabad", "state": "Gujarat", "pincode": "380015", "address": "SG Highway, Prahlad Nagar"},
    {"city": "Jaipur", "state": "Rajasthan", "pincode": "302017", "address": "Malviya Nagar, JLN Marg"},
    {"city": "Kochi", "state": "Kerala", "pincode": "682011", "address": "MG Road, Ernakulam"}
]

ENTERPRISES_POOL = [
    {"name": "Nexus Media Studios", "code": "NEXUS", "tax_id": "GSTIN29NEXUS1234F", "credit_limit": 1000000.0},
    {"name": "Red Chillies Production House", "code": "REDCH", "tax_id": "GSTIN27REDCH5678G", "credit_limit": 2500000.0},
    {"name": "Zerodha Creative Labs", "code": "ZEROC", "tax_id": "GSTIN29ZEROC9012H", "credit_limit": 1500000.0},
    {"name": "Phantom Films Collective", "code": "PHANT", "tax_id": "GSTIN27PHANT3456I", "credit_limit": 800000.0},
    {"name": "YRF Digital Media Division", "code": "YRFDM", "tax_id": "GSTIN27YRFDM7890J", "credit_limit": 3000000.0}
]

PRODUCT_CATALOG = [
    # Electronics & Cameras
    {"name": "Sony FX3 Cinema Line Camera", "slug": "sony-fx3", "category_slug": "electronics", "daily_rate": 3500, "purchase_price": 350000, "deposit_pct": 25},
    {"name": "RED Komodo 6K Cinema Camera", "slug": "red-komodo-6k", "category_slug": "electronics", "daily_rate": 6500, "purchase_price": 600000, "deposit_pct": 30},
    {"name": "ARRI Alexa Mini LF Rig", "slug": "arri-alexa-mini", "category_slug": "electronics", "daily_rate": 15000, "purchase_price": 4500000, "deposit_pct": 20},
    {"name": "Blackmagic Pocket Cinema 6K Pro", "slug": "bmpcc-6k-pro", "category_slug": "electronics", "daily_rate": 2500, "purchase_price": 240000, "deposit_pct": 25},
    {"name": "Canon EOS C300 Mark III", "slug": "canon-c300-mk3", "category_slug": "electronics", "daily_rate": 4500, "purchase_price": 450000, "deposit_pct": 25},
    {"name": "Sony A7S III Mirrorless Camera", "slug": "sony-a7s3", "category_slug": "electronics", "daily_rate": 2000, "purchase_price": 330000, "deposit_pct": 25},
    {"name": "DJI Ronin 4D 8K Cinema Combo", "slug": "dji-ronin-4d", "category_slug": "electronics", "daily_rate": 8000, "purchase_price": 850000, "deposit_pct": 25},
    {"name": "MacBook Pro 16 M3 Max Studio", "slug": "mbp-16-m3-max", "category_slug": "electronics", "daily_rate": 1800, "purchase_price": 380000, "deposit_pct": 20},

    # Furniture
    {"name": "Herman Miller Aeron Executive Chair", "slug": "herman-miller-aeron-exec", "category_slug": "furniture", "daily_rate": 200, "purchase_price": 140000, "deposit_pct": 20},
    {"name": "Steelcase Gesture Ergonomic Chair", "slug": "steelcase-gesture", "category_slug": "furniture", "daily_rate": 180, "purchase_price": 110000, "deposit_pct": 20},
    {"name": "Dual Motor Electric Standing Desk", "slug": "electric-standing-desk", "category_slug": "furniture", "daily_rate": 120, "purchase_price": 55000, "deposit_pct": 20},
    {"name": "Chesterfield Leather 3-Seater Sofa", "slug": "chesterfield-sofa", "category_slug": "furniture", "daily_rate": 350, "purchase_price": 120000, "deposit_pct": 25},

    # Vehicles
    {"name": "Toyota Innova Crysta ZX Auto", "slug": "innova-crysta-zx", "category_slug": "vehicles", "daily_rate": 2800, "purchase_price": 2600000, "deposit_pct": 15},
    {"name": "Mahindra Thar LX Hard Top 4x4", "slug": "mahindra-thar-4x4", "category_slug": "vehicles", "daily_rate": 3200, "purchase_price": 1700000, "deposit_pct": 15},
    {"name": "Force Traveller 17-Seater Luxury", "slug": "force-traveller-17", "category_slug": "vehicles", "daily_rate": 4500, "purchase_price": 2200000, "deposit_pct": 15},
    {"name": "Ather 450X Gen 3 Electric Scooter", "slug": "ather-450x-gen3", "category_slug": "vehicles", "daily_rate": 450, "purchase_price": 150000, "deposit_pct": 20},

    # Tools & Heavy Machinery
    {"name": "Bosch Heavy Duty Rotary Hammer Drill", "slug": "bosch-rotary-hammer", "category_slug": "tools", "daily_rate": 120, "purchase_price": 18000, "deposit_pct": 25},
    {"name": "DeWalt Cordless Circular Saw Kit", "slug": "dewalt-cordless-saw", "category_slug": "tools", "daily_rate": 150, "purchase_price": 22000, "deposit_pct": 25},
    {"name": "JCB 3DX Backhoe Excavator Loader", "slug": "jcb-3dx-excavator", "category_slug": "construction-equipment", "daily_rate": 6000, "purchase_price": 3800000, "deposit_pct": 10},
    {"name": "Hydraulic Mobile Crane 15T", "slug": "mobile-crane-15t", "category_slug": "construction-equipment", "daily_rate": 9000, "purchase_price": 5500000, "deposit_pct": 10},

    # Event Supplies
    {"name": "30x50ft Heavy Weatherproof German Tent", "slug": "german-tent-30x50", "category_slug": "event-supplies", "daily_rate": 3500, "purchase_price": 350000, "deposit_pct": 20},
    {"name": "JBL VTX A12 Line Array Sound System", "slug": "jbl-vtx-sound-system", "category_slug": "event-supplies", "daily_rate": 12000, "purchase_price": 2800000, "deposit_pct": 20},

    # Sports
    {"name": "Commercial Gym Treadmill LifeFitness", "slug": "lifefitness-treadmill", "category_slug": "sports-recreation", "daily_rate": 400, "purchase_price": 250000, "deposit_pct": 15},
    {"name": "Peloton Interactive Bike Studio", "slug": "peloton-bike-studio", "category_slug": "sports-recreation", "daily_rate": 300, "purchase_price": 180000, "deposit_pct": 20}
]

SOFTWARE_SERVICES_POOL = [
    {"name": "Adobe Creative Cloud All Apps License", "slug": "adobe-cc-all-apps", "monthly_rate": 4500, "quota": 1000},
    {"name": "DaVinci Resolve Studio Dongle License", "slug": "davinci-resolve-studio", "monthly_rate": 2500, "quota": 500},
    {"name": "Unreal Engine Enterprise Cloud Compute Node", "slug": "unreal-engine-compute", "monthly_rate": 12000, "quota": 5000},
    {"name": "Midjourney Pro API Quota (10k Fast Hrs)", "slug": "midjourney-pro-api", "monthly_rate": 8000, "quota": 10000},
    {"name": "AWS EC2 g5.12xlarge GPU Server Instance", "slug": "aws-ec2-g5-gpu", "monthly_rate": 25000, "quota": 20000}
]

DISPUTE_REASONS = [
    "Scratches found on lens element upon return",
    "Missing HDMI cable and original battery charger",
    "Late return without prior extension request",
    "Unit returned with damaged carrying case zip",
    "Water droplet residue inside battery compartment"
]

NOTIF_TEMPLATES = [
    "Your rental for {product} has been confirmed!",
    "Reminder: {product} is due for return tomorrow at 5:00 PM.",
    "Payment of ₹{amount} received for invoice #{invoice}.",
    "Deposit deduction notice issued for rental #{rental}.",
    "Your trust score increased by {points} points!"
]
