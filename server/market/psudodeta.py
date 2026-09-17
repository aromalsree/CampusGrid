from typing import Any, Dict, List
from django.utils.text import slugify


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
        'image_url': 'images/marketplace/products/macbook-pro.jpg',
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
        'image_url': 'images/marketplace/products/calculus-textbook.jpg',
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
        'image_url': 'images/marketplace/products/handwritten-notes.jpg',
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
        'image_url': 'images/marketplace/products/scientific-calculator.jpg',
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
        'image_url': 'images/marketplace/products/ipad-air.jpg',
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
        'image_url': 'images/marketplace/products/chemistry-book.jpg',
        'in_wishlist': False,
        'description': 'Karthekeyan & Mehta edition. Detailed reaction mechanisms and spectrometry problem sheets included.',
        'seller': {
            'username': 'ananya_chem',
            'institution': 'Faculty of Chemistry',
            'is_verified': True,
            'phone': '+919876543215'
        }
    },
    {
        'id': 7,
        'slug': 'arduino-starter-lab-kit',
        'title': 'Arduino Starter Lab Kit with Sensors',
        'price': '1,200',
        'condition': 'Good Condition',
        'campus': 'Innovation Lab',
        'category': 'lab-gear',
        'listing_type': 'SELL',
        'image_url': 'images/marketplace/products/lab-kit.jpg',
        'in_wishlist': False,
        'description': 'Arduino board, breadboard, jumper wires, LEDs, and common sensors for embedded systems coursework.',
        'seller': {
            'username': 'ishaan_embedded',
            'institution': 'Department of Electronics',
            'is_verified': True,
            'phone': '+919876543216'
        }
    },
    {
        'id': 8,
        'slug': 'hostel-study-lamp',
        'title': 'LED Study Lamp with USB Charging Port',
        'price': '650',
        'condition': 'Like New',
        'campus': 'North Hostel Block',
        'category': 'hostel',
        'listing_type': 'SELL',
        'image_url': 'images/marketplace/products/dorm-desk-lamp.jpg',
        'in_wishlist': False,
        'description': 'Adjustable warm and cool LED desk lamp with a compact base, perfect for late-night hostel study sessions.',
        'seller': {
            'username': 'meera_hostel',
            'institution': 'School of Design',
            'is_verified': True,
            'phone': '+919876543217'
        }
    },
    {
        'id': 9,
        'slug': 'campus-commuter-bicycle',
        'title': 'Hybrid Campus Commuter Bicycle',
        'price': '4,800',
        'condition': 'Good Condition',
        'campus': 'Sports Complex Gate',
        'category': 'mobility',
        'listing_type': 'SELL',
        'image_url': 'images/marketplace/products/campus-bicycle.jpg',
        'in_wishlist': False,
        'description': 'Lightweight hybrid bicycle with recently serviced brakes and gears. Includes a lock and rear light.',
        'seller': {
            'username': 'karthik_campus',
            'institution': 'Mechanical Engineering',
            'is_verified': True,
            'phone': '+919876543218'
        }
    },
    {
        'id': 10,
        'slug': 'python-peer-tutoring',
        'title': 'Python & Data Structures Peer Tutoring',
        'price': '300',
        'condition': 'Like New',
        'campus': 'Computer Science Block',
        'category': 'services',
        'listing_type': 'SERVICE',
        'image_url': 'images/marketplace/products/peer-tutoring.jpg',
        'in_wishlist': False,
        'description': 'One-hour peer tutoring sessions covering Python fundamentals, recursion, trees, graphs, and interview practice.',
        'seller': {
            'username': 'neha_codes',
            'institution': 'Department of Computer Science',
            'is_verified': True,
            'phone': '+919876543219'
        }
    },
    {
        'id': 11,
        'slug': 'resume-review-service',
        'title': 'Resume Review & Internship Profile Help',
        'price': '250',
        'condition': 'Like New',
        'campus': 'Career Centre',
        'category': 'services',
        'listing_type': 'SERVICE',
        'image_url': 'images/marketplace/products/study-coaching.jpg',
        'in_wishlist': False,
        'description': 'Friendly peer review of resumes, project descriptions, LinkedIn profiles, and internship applications.',
        'seller': {
            'username': 'aarav_careers',
            'institution': 'Business and Technology School',
            'is_verified': True,
            'phone': '+919876543220'
        }
    },
]


def _additional_products(start_id: int, category: str, image_url: str, titles: List[str]) -> List[Dict[str, Any]]:
    products = []
    for offset, title in enumerate(titles):
        products.append({
            'id': start_id + offset,
            'slug': slugify(title),
            'title': title,
            'price': str(300 + (offset * 175)),
            'condition': 'Good Condition',
            'campus': 'Campus Marketplace',
            'category': category,
            'listing_type': 'SERVICE' if category == 'services' else 'SELL',
            'image_url': image_url,
            'in_wishlist': False,
            'description': f'{title} available from a verified campus peer for the current semester.',
            'seller': {
                'username': f'{category.replace("-", "_")}_seller_{offset + 1}',
                'institution': 'Campus University',
                'is_verified': True,
                'phone': f'+9198765432{21 + start_id + offset:02d}',
            },
        })
    return products


SAMPLE_PRODUCTS.extend([
    *_additional_products(12, 'laptops', 'images/marketplace/products/macbook-pro.jpg', [
        'Dell XPS 13 Student Edition',
        'Lenovo ThinkPad T480 Laptop',
        'Samsung Galaxy Tab for Notes',
    ]),
    *_additional_products(15, 'books', 'images/marketplace/products/calculus-textbook.jpg', [
        'Engineering Mathematics Practice Set',
        'Introduction to Algorithms Study Guide',
        'Physics for Scientists and Engineers',
        'Database Systems Course Textbook',
    ]),
    *_additional_products(19, 'notes', 'images/marketplace/products/handwritten-notes.jpg', [
        'Operating Systems Exam Revision Notes',
        'Computer Networks Quick Revision Sheets',
        'Engineering Mathematics Formula Notes',
        'Digital Electronics Handwritten Notes',
        'Machine Learning Interview Notes',
    ]),
    *_additional_products(24, 'lab-gear', 'images/marketplace/products/lab-kit.jpg', [
        'Digital Multimeter for Electronics Lab',
        'Breadboard and Jumper Wire Experiment Kit',
        'Physics Optics Lab Equipment Set',
        'Soldering Iron and Precision Tool Kit',
        'Raspberry Pi GPIO Learning Kit',
    ]),
    *_additional_products(29, 'hostel', 'images/marketplace/products/dorm-desk-lamp.jpg', [
        'Compact Study Desk for Hostel Room',
        'Ergonomic Hostel Chair',
        'USB Rechargeable Table Fan',
        'Single Bed Storage Organizer',
        'Electric Kettle for Hostel Kitchen',
    ]),
    *_additional_products(34, 'mobility', 'images/marketplace/products/campus-bicycle.jpg', [
        'Single Speed Campus Bicycle',
        'Bicycle Helmet and Lock Set',
        'Foldable Bicycle for Students',
        'Campus Bicycle Front Basket',
        'LED Bicycle Safety Light Set',
    ]),
    *_additional_products(39, 'services', 'images/marketplace/products/peer-tutoring.jpg', [
        'Java Programming Peer Tutoring',
        'Calculus Exam Preparation Session',
        'SQL and Database Assignment Help',
        'Engineering Drawing Peer Workshop',
    ]),
])

SAMPLE_CATEGORIES: List[Dict[str, Any]] = [
    {'name': 'Laptops & Electronics', 'slug': 'laptops', 'count': 18},
    {'name': 'Textbooks & Study Guides', 'slug': 'books', 'count': 42},
    {'name': 'Academic Notes & PDFs', 'slug': 'notes', 'count': 29},
    {'name': 'Lab Gear & Instruments', 'slug': 'lab-gear', 'count': 15},
    {'name': 'Hostel & Room Essentials', 'slug': 'hostel', 'count': 21},
    {'name': 'Bicycles & Mobility', 'slug': 'mobility', 'count': 8},
    {'name': 'Peer Tutoring & Services', 'slug': 'services', 'count': 12},
]
