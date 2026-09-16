# Default sample catalog for campus marketplace when database models are not yet populated
SAMPLE_PRODUCTS: List[Dict[str, Any]] = [
    {
        'id': 1,
        'slug': 'macbook-pro-m1',
        'title': 'MacBook Pro M1 (16GB, 512GB)',
        'price': '58,000',
        'condition': 'Excellent Condition',
        'campus': 'North Quad / Tech Block',
        'category': 'laptops',
        'listing_type': 'SELL',
        'in_wishlist': False,
        'description': 'Gently used for 2 semesters of coursework. Battery health is at 91%. Comes with original 67W charger and box. Perfect for CS/IT students needing a fast build machine.',
        'seller': {
            'username': 'alex_cs',
            'institution': 'Department of Computer Science',
            'is_verified': True,
            'phone': '+919876543210'
        }
    },
    {
        'id': 2,
        'slug': 'calculus-early-transcendentals',
        'title': 'Calculus: Early Transcendentals (8th Ed.)',
        'price': '450',
        'condition': 'Good Condition',
        'campus': 'Central Library',
        'category': 'books',
        'listing_type': 'SELL',
        'in_wishlist': False,
        'description': 'Standard Stewart Calculus textbook. Minor pencil annotations in chapters 3 and 4, all problem sets and formula inserts intact.',
        'seller': {
            'username': 'sarah_m',
            'institution': 'School of Mathematics',
            'is_verified': True,
            'phone': '+919876543211'
        }
    },
    {
        'id': 3,
        'slug': 'dsa-handwritten-notes',
        'title': 'Data Structures & Algorithms Handwritten Notes',
        'price': '150',
        'condition': 'Like New',
        'campus': 'Academic Block B',
        'category': 'notes',
        'listing_type': 'SELL',
        'in_wishlist': False,
        'description': 'Comprehensive revision sheets covering Trees, Graphs, DP, and Greedy algorithms with clean color-coded diagrams and Big-O derivations.',
        'seller': {
            'username': 'rahul_k',
            'institution': 'Dept of Information Technology',
            'is_verified': True,
            'phone': '+919876543212'
        }
    },
    {
        'id': 4,
        'slug': 'casio-fx-991ex',
        'title': 'Casio FX-991EX ClassWiz Scientific Calculator',
        'price': '80',
        'condition': 'Good Condition',
        'campus': 'Engineering Quad',
        'category': 'laptops',
        'listing_type': 'RENTAL',
        'in_wishlist': False,
        'description': 'Permitted in university examinations. Solar cell and battery functional. Available for exam week or full semester rental.',
        'seller': {
            'username': 'priya_ee',
            'institution': 'Dept of Electrical Engineering',
            'is_verified': True,
            'phone': '+919876543213'
        }
    },
    {
        'id': 5,
        'slug': 'ipad-air-5th-gen',
        'title': 'iPad Air 5th Gen (64GB, Wi-Fi, Space Gray)',
        'price': '38,500',
        'condition': 'Like New',
        'campus': 'Main Campus Hostels',
        'category': 'laptops',
        'listing_type': 'SELL',
        'in_wishlist': False,
        'description': 'M1 chip with Apple Pencil 2 support. Always kept in tempered glass screen protector and magnetic case. Ideal for paperless notes.',
        'seller': {
            'username': 'david_bio',
            'institution': 'Biomedical Engineering',
            'is_verified': False,
            'phone': '+919876543214'
        }
    },
    {
        'id': 6,
        'slug': 'organic-chemistry-mechanisms',
        'title': 'Organic Chemistry: Principles & Mechanisms',
        'price': '520',
        'condition': 'Good Condition',
        'campus': 'Science Block A',
        'category': 'books',
        'listing_type': 'SELL',
        'in_wishlist': False,
        'description': 'Karthekeyan & Mehta edition. Detailed reaction mechanisms and spectrometry problem sheets included.',
        'seller': {
            'username': 'ananya_chem',
            'institution': 'Faculty of Chemistry',
            'is_verified': True,
            'phone': '+919876543215'
        }
    },
]

SAMPLE_CATEGORIES: List[Dict[str, Any]] = [
    {'name': 'Laptops & Electronics', 'slug': 'laptops', 'count': 18},
    {'name': 'Textbooks & Study Guides', 'slug': 'books', 'count': 42},
    {'name': 'Academic Notes & PDFs', 'slug': 'notes', 'count': 29},
    {'name': 'Lab Gear & Instruments', 'slug': 'lab-gear', 'count': 15},
    {'name': 'Hostel & Room Essentials', 'slug': 'hostel', 'count': 21},
    {'name': 'Bicycles & Mobility', 'slug': 'mobility', 'count': 8},
]
