import os
from decimal import Decimal
from PIL import Image, ImageDraw
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from marketplace.models import (
    UserProfile, Category, Product, ProductImage,
    ElectronicsSpecification, SemesterBundle, BundleItem,
    StudentRequest, Review, Notification
)

def create_product_graphic(filename, title, specs, category_tag, bg_color, accent_color, badge_text, icon_symbol):
    """Generates a high-resolution stylized product artwork banner using Pillow."""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Ambient mesh circles
    for r in range(260, 20, -15):
        alpha_fill = tuple(min(255, int(c * (1 - r/320))) for c in accent_color)
        draw.ellipse([width//2 - r*1.4, height//2 - r*0.9, width//2 + r*1.4, height//2 + r*0.9], fill=alpha_fill)

    # Outer decorative card frame
    draw.rounded_rectangle([24, 24, width - 24, height - 24], radius=28, outline=(51, 65, 85), width=2)
    draw.rounded_rectangle([32, 32, width - 32, height - 32], radius=24, outline=(30, 41, 59), width=1)

    # Category Pill Header
    draw.rounded_rectangle([50, 50, 280, 92], radius=14, fill=(15, 23, 42), outline=accent_color, width=2)
    draw.text((68, 62), category_tag, fill=(241, 245, 249))

    # Badge Pill
    draw.rounded_rectangle([width - 240, 50, width - 50, 92], radius=14, fill=(15, 23, 42), outline=(16, 185, 129), width=1)
    draw.text((width - 220, 62), badge_text, fill=(52, 211, 153))

    # Center Hero Hardware / Graphic Canvas
    draw.rounded_rectangle([200, 130, width - 200, height - 190], radius=24, fill=(15, 23, 42), outline=(71, 85, 105), width=3)
    
    # Stylized Inner Screen / Frame
    draw.rounded_rectangle([220, 150, width - 220, height - 210], radius=16, fill=(9, 13, 22), outline=(30, 41, 59), width=2)
    draw.text((width//2 - 60, height//2 - 40), icon_symbol, fill=(248, 250, 252))

    # Bottom Information Canvas
    draw.rounded_rectangle([50, height - 165, width - 50, height - 50], radius=18, fill=(15, 23, 42), outline=(51, 65, 85), width=1)
    draw.text((70, height - 150), title[:52], fill=(255, 255, 255))
    draw.text((70, height - 115), specs[:65], fill=(148, 163, 184))
    draw.text((70, height - 85), "CAMPUSGRID VERIFIED LISTING • DIRECT HOSTEL HANDOVER • 0% FEES", fill=(52, 211, 153))

    media_dir = os.path.join(settings.BASE_DIR, 'media')
    target_path = os.path.join(media_dir, filename)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    img.save(target_path, format='JPEG', quality=94)
    return target_path


class Command(BaseCommand):
    help = "Seeds the database with rich, realistic campus marketplace listings and local images"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CampusGrid database with rich product imagery...")

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@campus.edu", "is_staff": True, "is_superuser": True}
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            UserProfile.objects.get_or_create(user=admin_user, defaults={"campus": "IIT Bombay", "verification_status": "VERIFIED", "whatsapp_number": "919876543210"})

        # 2. Student Demo Users
        students_data = [
            {"username": "alex_cs", "name": "Alex Chen", "email": "alex.chen@mit.edu", "campus": "IIT Bombay", "wa": "919811223344", "status": "VERIFIED"},
            {"username": "priya_ee", "name": "Priya Sharma", "email": "priya.s@bits-pilani.ac.in", "campus": "BITS Pilani", "wa": "919822334455", "status": "VERIFIED"},
            {"username": "rahul_mech", "name": "Rahul Verma", "email": "rahul.v@nitc.ac.in", "campus": "NIT Trichy", "wa": "919833445566", "status": "PENDING"},
            {"username": "ananya_ds", "name": "Ananya Roy", "email": "ananya.r@iiitd.ac.in", "campus": "IIIT Delhi", "wa": "919844556677", "status": "VERIFIED"},
            {"username": "kavita_ce", "name": "Kavita Nair", "email": "kavita.n@dtu.ac.in", "campus": "Delhi Tech Univ", "wa": "919855667788", "status": "VERIFIED"},
        ]

        users = {}
        for s in students_data:
            u, _ = User.objects.get_or_create(
                username=s["username"],
                defaults={"email": s["email"], "first_name": s["name"].split()[0], "last_name": s["name"].split()[1] if len(s["name"].split()) > 1 else ""}
            )
            u.set_password("campus123")
            u.save()
            UserProfile.objects.get_or_create(user=u, defaults={"campus": s["campus"], "whatsapp_number": s["wa"], "verification_status": s["status"]})
            users[s["username"]] = u

        # 3. Categories
        categories_data = [
            {"name": "Laptops & Electronics", "slug": "laptops-electronics", "icon": "laptop", "desc": "Pre-owned laptops, tablets, chargers, and calculators"},
            {"name": "Textbooks & Reference Books", "slug": "textbooks-books", "icon": "book-open", "desc": "Standard semester course textbooks and reference guides"},
            {"name": "Lab & Engineering Tools", "slug": "lab-engineering-tools", "icon": "cpu", "desc": "Mini drafters, lab coats, multimeter, and breadboards"},
            {"name": "Study Notes & Digital Assets", "slug": "notes-digital-assets", "icon": "file-text", "desc": "Handwritten semester toppers notes and solved past papers"},
            {"name": "Academic Services & Mentorship", "slug": "academic-services", "icon": "graduation-cap", "desc": "Peer coding guidance, project review, and math coaching"},
            {"name": "Dorm & Cycle Essentials", "slug": "dorm-cycle-essentials", "icon": "bike", "desc": "Campus bicycles, study lamps, kettles, and mattress"},
        ]

        cats = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=c["slug"],
                defaults={"name": c["name"], "icon": c["icon"], "description": c["desc"]}
            )
            cats[c["slug"]] = cat

        # 4. Products with Generated Product Graphics
        products_catalog = [
            {
                "slug": "apple-macbook-air-m1-2020-space-grey",
                "title": "Apple MacBook Air M1 (2020, 8GB / 256GB SSD, Space Grey)",
                "seller": users["alex_cs"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("54000.00"),
                "rent_daily_rate": Decimal("350.00"),
                "condition": "LIKE_NEW",
                "campus": "IIT Bombay",
                "is_urgent": True,
                "description": "Mint condition MacBook Air M1 used for CS coding assignments. Battery health is at 94% with 112 cycles. Comes with original 30W Apple charger and box.",
                "img_file": "products/macbook_air_m1.jpg",
                "img_tag": "LAPTOP / APPLE",
                "img_badge": "LIKE NEW 94%",
                "img_icon": "MACBOOK M1",
                "bg_color": (9, 13, 22),
                "accent_color": (16, 185, 129),
                "specs": {
                    "processor": "Apple M1 8-Core CPU",
                    "ram_gb": 8,
                    "storage_gb": 256,
                    "storage_type": "NVME_SSD",
                    "battery_health_percent": 94,
                    "usage_duration_months": 14,
                    "display_specs": "13.3-inch Retina Display (2560x1600)",
                    "graphics": "Apple 7-Core GPU",
                    "operating_system": "macOS Sonoma",
                    "extra_specs": "112 Battery Cycle Count, Original 30W USB-C brick included"
                }
            },
            {
                "slug": "dell-xps-13-9305-intel-core-i7-16gb",
                "title": "Dell XPS 13 9305 (Intel Core i7 11th Gen, 16GB / 512GB SSD)",
                "seller": users["rahul_mech"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BUY",
                "price": Decimal("51000.00"),
                "rent_daily_rate": None,
                "condition": "LIKE_NEW",
                "campus": "IIT Bombay",
                "is_urgent": False,
                "description": "Powerful ultrabook with 16GB RAM for CAD, SolidWorks, and virtualization. Battery health is 88%. Clean carbon fiber palmrest with charger.",
                "img_file": "products/dell_xps_13.jpg",
                "img_tag": "LAPTOP / DELL",
                "img_badge": "16GB RAM / i7",
                "img_icon": "DELL XPS 13",
                "bg_color": (15, 23, 42),
                "accent_color": (56, 189, 248),
                "specs": {
                    "processor": "Intel Core i7-1165G7 Quad-Core",
                    "ram_gb": 16,
                    "storage_gb": 512,
                    "storage_type": "NVME_SSD",
                    "battery_health_percent": 88,
                    "usage_duration_months": 18,
                    "display_specs": "13.3-inch FHD+ InfinityEdge IPS",
                    "graphics": "Intel Iris Xe Graphics",
                    "operating_system": "Windows 11 Pro",
                    "extra_specs": "65W Type-C Fast Charger"
                }
            },
            {
                "slug": "lenovo-thinkpad-t14-gen2-amd",
                "title": "Lenovo ThinkPad T14 Gen 2 (Ryzen 7 Pro, 16GB / 512GB NVMe)",
                "seller": users["ananya_ds"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("46500.00"),
                "rent_daily_rate": Decimal("280.00"),
                "condition": "LIKE_NEW",
                "campus": "IIIT Delhi",
                "is_urgent": False,
                "description": "Legendary ThinkPad keyboard and durability. Ryzen 7 5850U with 8 cores / 16 threads. Dual battery system with 92% health.",
                "img_file": "products/thinkpad_t14.jpg",
                "img_tag": "LAPTOP / LENOVO",
                "img_badge": "RYZEN 7 PRO",
                "img_icon": "THINKPAD T14",
                "bg_color": (15, 23, 42),
                "accent_color": (239, 68, 68),
                "specs": {
                    "processor": "AMD Ryzen 7 PRO 5850U 8-Core",
                    "ram_gb": 16,
                    "storage_gb": 512,
                    "storage_type": "NVME_SSD",
                    "battery_health_percent": 92,
                    "usage_duration_months": 12,
                    "display_specs": "14.0-inch FHD Antiglare IPS (400 nits)",
                    "graphics": "AMD Radeon Vega 8",
                    "operating_system": "Ubuntu 22.04 LTS / Win 11",
                    "extra_specs": "Backlit keyboard, Fingerprint reader"
                }
            },
            {
                "slug": "apple-ipad-air-5th-gen-64gb-m1",
                "title": "Apple iPad Air 5th Gen (M1 Chip, 64GB Wi-Fi, Starlight)",
                "seller": users["priya_ee"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("38500.00"),
                "rent_daily_rate": Decimal("220.00"),
                "condition": "LIKE_NEW",
                "campus": "BITS Pilani",
                "is_urgent": True,
                "description": "Blazing fast M1 processor for GoodNotes, Procreate, and lectures. Paperlike screen protector pre-applied. Includes magnetic folio cover.",
                "img_file": "products/ipad_air5.jpg",
                "img_tag": "TABLET / APPLE",
                "img_badge": "M1 POWERED",
                "img_icon": "IPAD AIR 5",
                "bg_color": (9, 13, 22),
                "accent_color": (245, 158, 11),
                "specs": {
                    "processor": "Apple M1 Chip (8-Core CPU)",
                    "ram_gb": 8,
                    "storage_gb": 64,
                    "storage_type": "EMMC_OR_OTHER",
                    "battery_health_percent": 96,
                    "usage_duration_months": 8,
                    "display_specs": "10.9-inch Liquid Retina TrueTone",
                    "graphics": "Apple 8-Core GPU",
                    "operating_system": "iPadOS 17",
                    "extra_specs": "Apple Pencil 2 compatible"
                }
            },
            {
                "slug": "sony-wh-1000xm4-noise-cancelling-headphones",
                "title": "Sony WH-1000XM4 Wireless Noise Cancelling Headphones",
                "seller": users["alex_cs"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("14500.00"),
                "rent_daily_rate": Decimal("120.00"),
                "condition": "LIKE_NEW",
                "campus": "IIT Bombay",
                "is_urgent": False,
                "description": "Industry-leading active noise cancelling, perfect for noisy hostel study rooms and library sessions. Battery lasts 30+ hours on single charge.",
                "img_file": "products/sony_xm4.jpg",
                "img_tag": "AUDIO / SONY",
                "img_badge": "ANC 30HR BATTERY",
                "img_icon": "SONY WH-1000XM4",
                "bg_color": (15, 23, 42),
                "accent_color": (245, 158, 11),
                "specs": None
            },
            {
                "slug": "casio-fx-991ex-classwiz-calculator",
                "title": "Casio FX-991EX ClassWiz Non-Programmable Scientific Calculator",
                "seller": users["priya_ee"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("950.00"),
                "rent_daily_rate": Decimal("25.00"),
                "condition": "LIKE_NEW",
                "campus": "BITS Pilani",
                "is_urgent": False,
                "description": "Essential non-programmable calculator permitted in university exams. Solves matrix, integration, complex numbers, and quadratic equations.",
                "img_file": "products/casio_991ex.jpg",
                "img_tag": "CALCULATOR / CASIO",
                "img_badge": "EXAM APPROVED",
                "img_icon": "CASIO FX-991EX",
                "bg_color": (9, 13, 22),
                "accent_color": (16, 185, 129),
                "specs": None
            },
            {
                "slug": "ti-84-plus-ce-color-graphing-calculator",
                "title": "Texas Instruments TI-84 Plus CE Color Graphing Calculator",
                "seller": users["kavita_ce"],
                "category": cats["laptops-electronics"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("6800.00"),
                "rent_daily_rate": Decimal("60.00"),
                "condition": "LIKE_NEW",
                "campus": "Delhi Tech Univ",
                "is_urgent": False,
                "description": "High-resolution color backlit display with rechargeable battery. Ideal for advanced calculus, statistics, engineering curves, and Python programming.",
                "img_file": "products/ti_84_ce.jpg",
                "img_tag": "GRAPHING CALC",
                "img_badge": "COLOR BACKLIT",
                "img_icon": "TI-84 PLUS CE",
                "bg_color": (15, 23, 42),
                "accent_color": (56, 189, 248),
                "specs": None
            },
            {
                "slug": "operating-system-concepts-10th-edition-silberschatz",
                "title": "Operating System Concepts (10th Dinosaur Edition) — Silberschatz & Galvin",
                "seller": users["alex_cs"],
                "category": cats["textbooks-books"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BUY",
                "price": Decimal("490.00"),
                "rent_daily_rate": None,
                "condition": "LIKE_NEW",
                "campus": "IIT Bombay",
                "is_urgent": False,
                "description": "Standard university prescribed textbook for OS. Covers processes, threads, CPU scheduling, synchronization, and virtual memory. Zero marks or dog-ears.",
                "img_file": "products/os_silberschatz.jpg",
                "img_tag": "TEXTBOOK / CS",
                "img_badge": "10TH EDITION",
                "img_icon": "OS CONCEPTS",
                "bg_color": (15, 23, 42),
                "accent_color": (16, 185, 129),
                "specs": None
            },
            {
                "slug": "introduction-to-algorithms-clrs-4th-edition",
                "title": "Introduction to Algorithms (CLRS 4th Edition) — Cormen & Leiserson",
                "seller": users["ananya_ds"],
                "category": cats["textbooks-books"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BUY",
                "price": Decimal("850.00"),
                "rent_daily_rate": None,
                "condition": "LIKE_NEW",
                "campus": "IIIT Delhi",
                "is_urgent": False,
                "description": "The definitive bible of Algorithms. Pristine condition hardcover. Perfect for college curriculum and technical coding interview prep.",
                "img_file": "products/clrs_algorithms.jpg",
                "img_tag": "ALGORITHMS BIBLE",
                "img_badge": "CLRS 4TH ED",
                "img_icon": "CLRS ALGORITHMS",
                "bg_color": (9, 13, 22),
                "accent_color": (245, 158, 11),
                "specs": None
            },
            {
                "slug": "higher-engineering-mathematics-bs-grewal-44th-ed",
                "title": "Higher Engineering Mathematics — B.S. Grewal (44th Edition)",
                "seller": users["rahul_mech"],
                "category": cats["textbooks-books"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BUY",
                "price": Decimal("380.00"),
                "rent_daily_rate": None,
                "condition": "GOOD",
                "campus": "NIT Trichy",
                "is_urgent": True,
                "description": "Clean textbook with all formulas intact. No missing pages. Covers Calculus, Differential Equations, Matrices, and Vector Analysis.",
                "img_file": "products/bs_grewal_math.jpg",
                "img_tag": "TEXTBOOK / MATH",
                "img_badge": "ALL SEMESTERS",
                "img_icon": "B.S. GREWAL MATH",
                "bg_color": (15, 23, 42),
                "accent_color": (16, 185, 129),
                "specs": None
            },
            {
                "slug": "omega-engineering-drawing-mini-drafter-kit",
                "title": "Omega Deluxe Engineering Drawing Mini Drafter + Steel Scale + Sheet Container",
                "seller": users["priya_ee"],
                "category": cats["lab-engineering-tools"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("550.00"),
                "rent_daily_rate": Decimal("30.00"),
                "condition": "LIKE_NEW",
                "campus": "BITS Pilani",
                "is_urgent": False,
                "description": "Used only for one semester ED course. Steel clamps with zero wobble. Includes protective cylinder tube for drawing sheets.",
                "img_file": "products/mini_drafter.jpg",
                "img_tag": "LAB TOOL / ED",
                "img_badge": "ZERO WOBBLE",
                "img_icon": "MINI DRAFTER KIT",
                "bg_color": (9, 13, 22),
                "accent_color": (56, 189, 248),
                "specs": None
            },
            {
                "slug": "arduino-mega-robotics-starter-kit",
                "title": "Arduino Mega 2560 R3 Advanced Robotics Starter Kit + Breadboard & Sensors",
                "seller": users["kavita_ce"],
                "category": cats["lab-engineering-tools"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BOTH",
                "price": Decimal("1850.00"),
                "rent_daily_rate": Decimal("50.00"),
                "condition": "LIKE_NEW",
                "campus": "Delhi Tech Univ",
                "is_urgent": False,
                "description": "Complete lab kit with Arduino Mega, jumper wires, ultrasonic sensor, servo motors, LCD screen, and 830-point breadboard. Tested and working.",
                "img_file": "products/arduino_kit.jpg",
                "img_tag": "HARDWARE LAB",
                "img_badge": "COMPLETE SENSORS",
                "img_icon": "ARDUINO LAB KIT",
                "bg_color": (15, 23, 42),
                "accent_color": (16, 185, 129),
                "specs": None
            },
            {
                "slug": "dsa-complete-handwritten-notes-faang-prep",
                "title": "Data Structures & Algorithms Complete Handwritten Notes (Trees, Graphs, DP)",
                "seller": users["ananya_ds"],
                "category": cats["notes-digital-assets"],
                "product_type": "DIGITAL",
                "buy_or_rent": "BUY",
                "price": Decimal("149.00"),
                "rent_daily_rate": None,
                "condition": "NOT_APPLICABLE",
                "campus": "IIIT Delhi",
                "is_urgent": False,
                "description": "Neatly scanned colored PDF notes covering 150+ standard LeetCode problems with time/space complexity diagrams, dry runs, and code snippets.",
                "img_file": "products/dsa_notes_digital.jpg",
                "img_tag": "DIGITAL ASSET / PDF",
                "img_badge": "150+ LEETCODE",
                "img_icon": "DSA MASTER NOTES",
                "bg_color": (9, 13, 22),
                "accent_color": (16, 185, 129),
                "specs": None
            },
            {
                "slug": "machine-learning-end-to-end-project-repo",
                "title": "End-to-End Deep Learning & Computer Vision Major Project Codebase (PyTorch)",
                "seller": users["ananya_ds"],
                "category": cats["notes-digital-assets"],
                "product_type": "DIGITAL",
                "buy_or_rent": "BUY",
                "price": Decimal("249.00"),
                "rent_daily_rate": None,
                "condition": "NOT_APPLICABLE",
                "campus": "IIIT Delhi",
                "is_urgent": False,
                "description": "Production-ready PyTorch codebase with FastAPI deployment, dataset preprocessing scripts, and full 40-page project documentation report.",
                "img_file": "products/ml_project_repo.jpg",
                "img_tag": "SOURCE CODE & DOCS",
                "img_badge": "PYTORCH + FASTAPI",
                "img_icon": "ML PROJECT REPO",
                "bg_color": (15, 23, 42),
                "accent_color": (56, 189, 248),
                "specs": None
            },
            {
                "slug": "1-on-1-django-fullstack-mentorship",
                "title": "1-on-1 Full-Stack Web Dev & Django Major Project Mentorship",
                "seller": users["alex_cs"],
                "category": cats["academic-services"],
                "product_type": "SERVICE",
                "buy_or_rent": "BUY",
                "price": Decimal("299.00"),
                "rent_daily_rate": None,
                "service_rate_type": "PER_HOUR",
                "service_duration_info": "60 mins live screen share & architecture review",
                "condition": "NOT_APPLICABLE",
                "campus": "IIT Bombay",
                "is_urgent": False,
                "description": "Senior student offering 1-on-1 peer code review, architecture debugging, and viva preparation for college web development projects.",
                "img_file": "products/django_mentorship.jpg",
                "img_tag": "ACADEMIC SERVICE",
                "img_badge": "1-ON-1 LIVE",
                "img_icon": "PEER MENTORSHIP",
                "bg_color": (9, 13, 22),
                "accent_color": (16, 185, 129),
                "specs": None
            },
            {
                "slug": "hero-sprint-21-speed-geared-cycle",
                "title": "Hero Sprint Pro 21-Speed Geared Hybrid Bicycle + Number Lock",
                "seller": users["alex_cs"],
                "category": cats["dorm-cycle-essentials"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BUY",
                "price": Decimal("4200.00"),
                "rent_daily_rate": None,
                "condition": "GOOD",
                "campus": "IIT Bombay",
                "is_urgent": True,
                "description": "Graduating senior moving out! Smooth dual-disc brakes, Shimano Tourney gears, front suspension, and sturdy cable number lock included.",
                "img_file": "products/hero_bicycle.jpg",
                "img_tag": "DORM / CYCLE",
                "img_badge": "21-SPEED SHIMANO",
                "img_icon": "HERO BICYCLE",
                "bg_color": (15, 23, 42),
                "accent_color": (245, 158, 11),
                "specs": None
            },
            {
                "slug": "rechargeable-led-hostel-study-lamp",
                "title": "Wipro 3-Tone Dimming Rechargeable LED Study Desk Lamp (2000mAh)",
                "seller": users["priya_ee"],
                "category": cats["dorm-cycle-essentials"],
                "product_type": "PHYSICAL",
                "buy_or_rent": "BUY",
                "price": Decimal("450.00"),
                "rent_daily_rate": None,
                "condition": "LIKE_NEW",
                "campus": "BITS Pilani",
                "is_urgent": False,
                "description": "Eye-care warm/cool LED dimming. Flexible 360 neck with 6 hours battery backup during hostel power cuts. USB-C charging.",
                "img_file": "products/study_lamp.jpg",
                "img_tag": "DORM ESSENTIAL",
                "img_badge": "3-TONE DIMMING",
                "img_icon": "LED DESK LAMP",
                "bg_color": (9, 13, 22),
                "accent_color": (56, 189, 248),
                "specs": None
            },
        ]

        for pdata in products_catalog:
            # 1. Generate artwork
            img_path = create_product_graphic(
                filename=pdata["img_file"],
                title=pdata["title"],
                specs=pdata["description"],
                category_tag=pdata["img_tag"],
                bg_color=pdata["bg_color"],
                accent_color=pdata["accent_color"],
                badge_text=pdata["img_badge"],
                icon_symbol=pdata["img_icon"]
            )

            p, _ = Product.objects.get_or_create(
                slug=pdata["slug"],
                defaults={
                    "title": pdata["title"],
                    "seller": pdata["seller"],
                    "category": pdata["category"],
                    "product_type": pdata["product_type"],
                    "buy_or_rent": pdata["buy_or_rent"],
                    "price": pdata["price"],
                    "rent_daily_rate": pdata.get("rent_daily_rate"),
                    "service_rate_type": pdata.get("service_rate_type", "TOTAL"),
                    "service_duration_info": pdata.get("service_duration_info", ""),
                    "condition": pdata["condition"],
                    "campus": pdata["campus"],
                    "is_urgent": pdata["is_urgent"],
                    "is_available": True,
                    "description": pdata["description"],
                }
            )

            # Attach primary image
            with open(img_path, 'rb') as f:
                p.primary_image.save(os.path.basename(img_path), File(f), save=False)
                
            # If digital product, attach protected digital file
            if p.product_type == "DIGITAL":
                notes_doc = os.path.join(settings.BASE_DIR, 'media', 'dummy_notes.pdf')
                if not os.path.exists(notes_doc):
                    with open(notes_doc, 'wb') as df:
                        df.write(b"%PDF-1.4 CampusGrid Verified Academic Resource Demo Notes")
                with open(notes_doc, 'rb') as df:
                    p.digital_file.save("campusgrid_notes.pdf", File(df), save=False)
                    p.sample_preview_pdf.save("sample_preview.pdf", File(df), save=False)

            p.save()

            # Create specs if present
            if pdata.get("specs"):
                ElectronicsSpecification.objects.get_or_create(
                    product=p,
                    defaults=pdata["specs"]
                )

            # Secondary gallery image
            if ProductImage.objects.filter(product=p).count() == 0:
                ProductImage.objects.create(
                    product=p,
                    image=p.primary_image,
                    caption=f"{p.title} Preview"
                )

        # 5. Semester Bundles with Covers
        b1_img = create_product_graphic(
            filename="bundles/cs_sem4_bundle.jpg",
            title="Computer Science Sem 4 Complete Pass-Down Kit",
            specs="OS Concepts Book + Mini Drafter + DSA Master Notes",
            category_tag="SEMESTER BUNDLE",
            bg_color=(15, 23, 42),
            accent_color=(16, 185, 129),
            badge_text="SAVE 25% BUNDLE",
            icon_symbol="CS SEM 4 KIT"
        )
        b1, _ = SemesterBundle.objects.get_or_create(
            slug="cs-sem-4-core-pass-down-bundle-iitb",
            defaults={
                "title": "Computer Science Sem 4 Complete Pass-Down Kit (Textbooks + Notes + Lab)",
                "seller": users["alex_cs"],
                "semester": "Semester 4",
                "course": "Computer Science & Engineering",
                "campus": "IIT Bombay",
                "price": Decimal("950.00"),
                "description": "Everything you need for Sem 4 CS! Includes Silberschatz OS textbook, DSA master revision notes, and lab breadboard kit. Save 25% compared to buying individually!",
                "is_available": True,
            }
        )
        with open(b1_img, 'rb') as f:
            b1.cover_image.save(os.path.basename(b1_img), File(f), save=True)

        # Bundle items
        BundleItem.objects.get_or_create(bundle=b1, title="Operating System Concepts 10th Ed Textbook", defaults={"item_type": "BOOK", "notes": "Silberschatz Dinosaur Book"})
        BundleItem.objects.get_or_create(bundle=b1, title="DSA Complete Master Handwritten Notes PDF", defaults={"item_type": "NOTES", "notes": "150+ LeetCode Solutions"})

        # Bundle 2: Mechanical 1st Year Engineering Kit
        b2_img = create_product_graphic(
            filename="bundles/mech_sem1_bundle.jpg",
            title="1st Year Engineering Drawing & Lab Starter Kit",
            specs="Mini Drafter + B.S. Grewal Math + Casio Calculator",
            category_tag="SEMESTER BUNDLE",
            bg_color=(9, 13, 22),
            accent_color=(245, 158, 11),
            badge_text="FRESHERS SPECIAL",
            icon_symbol="1ST YEAR KIT"
        )
        b2, _ = SemesterBundle.objects.get_or_create(
            slug="1st-year-engineering-fresher-survival-bundle",
            defaults={
                "title": "1st Year Freshers Complete Engineering Drawing & Math Kit",
                "seller": users["priya_ee"],
                "semester": "Semester 1 & 2",
                "course": "All Engineering Branches",
                "campus": "BITS Pilani",
                "price": Decimal("1650.00"),
                "description": "Essential bundle for freshers: Omega Mini Drafter with container, B.S. Grewal Higher Mathematics, and Casio fx-991EX Calculator.",
                "is_available": True,
            }
        )
        with open(b2_img, 'rb') as f:
            b2.cover_image.save(os.path.basename(b2_img), File(f), save=True)

        BundleItem.objects.get_or_create(bundle=b2, title="Omega Deluxe Mini Drafter Kit", defaults={"item_type": "LAB_TOOL", "notes": "With sheet container"})
        BundleItem.objects.get_or_create(bundle=b2, title="B.S. Grewal Higher Engineering Mathematics", defaults={"item_type": "BOOK", "notes": "44th edition"})
        BundleItem.objects.get_or_create(bundle=b2, title="Casio FX-991EX Calculator", defaults={"item_type": "OTHER", "notes": "Non-programmable"})

        # 6. Student Need Board Requests
        StudentRequest.objects.get_or_create(
            title="Looking for TI-84 Plus CE Graphing Calculator for Calculus 3",
            requester=users["priya_ee"],
            defaults={
                "category": cats["laptops-electronics"],
                "campus": "BITS Pilani",
                "max_budget": Decimal("5500.00"),
                "description": "Need a clean working TI-84 color calculator for upcoming mid-term exams. Ready for immediate cash or UPI payment on campus.",
                "contact_preference": "WHATSAPP",
                "status": "OPEN",
            }
        )

        StudentRequest.objects.get_or_create(
            title="Looking to rent Apple Pencil 2nd Gen for 2 weeks during design jury",
            requester=users["ananya_ds"],
            defaults={
                "category": cats["laptops-electronics"],
                "campus": "IIIT Delhi",
                "max_budget": Decimal("500.00"),
                "description": "Need Apple Pencil 2 for iPad Air during submission week. Will return in pristine condition.",
                "contact_preference": "IN_APP",
                "status": "OPEN",
            }
        )

        StudentRequest.objects.get_or_create(
            title="Urgent: Need Operating Systems (Silberschatz) Hardcopy Book",
            requester=users["rahul_mech"],
            defaults={
                "category": cats["textbooks-books"],
                "campus": "NIT Trichy",
                "max_budget": Decimal("400.00"),
                "description": "Looking for 9th or 10th edition. Can collect today from Diamond Hostel.",
                "contact_preference": "WHATSAPP",
                "status": "OPEN",
            }
        )

        # 7. Reviews
        p_os = Product.objects.get(slug="operating-system-concepts-10th-edition-silberschatz")
        p_dsa = Product.objects.get(slug="dsa-complete-handwritten-notes-faang-prep")
        Review.objects.get_or_create(
            reviewer=users["priya_ee"],
            product=p_os,
            defaults={
                "rating": 5,
                "comment": "Alex is an awesome senior! The OS textbook was exactly as described, completely clean with zero marks. Super fast handover at the hostel gate.",
                "is_verified_purchase": True
            }
        )

        Review.objects.get_or_create(
            reviewer=users["alex_cs"],
            product=p_dsa,
            defaults={
                "rating": 5,
                "comment": "The handwritten DSA notes are top quality. The graph traversal diagrams and DP recurrence relations made my exam prep 10x easier!",
                "is_verified_purchase": True
            }
        )

        # 8. Notifications
        Notification.objects.get_or_create(
            user=users["alex_cs"],
            title="Student Request Matched!",
            defaults={
                "message": "A student in your campus is looking for a Graphing Calculator matching your listings.",
                "notification_type": "MATCHING_REQUEST",
                "link": "/requests/",
                "is_read": False,
            }
        )

        Notification.objects.get_or_create(
            user=users["alex_cs"],
            title="New 5-Star Review Received",
            defaults={
                "message": "Priya Sharma left a 5-star review on your listing 'Operating System Concepts'.",
                "notification_type": "REVIEW",
                "link": "/profile/",
                "is_read": True,
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded CampusGrid with rich product listings and Pillow-generated local imagery!"))
