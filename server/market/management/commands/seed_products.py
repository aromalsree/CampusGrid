import os
import shutil
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from market.models import Category, Listing, ListingImage

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the marketplace so every category has at least 6 products with high-quality images and descriptions."

    def handle(self, *args, **options):
        self.stdout.write("Ensuring marketplace categories and media directory...")

        media_images_dir = os.path.join(settings.MEDIA_ROOT, "listings", "images")
        os.makedirs(media_images_dir, exist_ok=True)
        static_products_dir = os.path.join(settings.BASE_DIR, "static", "images", "marketplace", "products")
        static_market_dir = os.path.join(settings.BASE_DIR, "static", "images", "marketplace")

        # 1. Ensure active categories exist
        category_specs = [
            ("Laptops & Electronics", "laptops", "Laptops, gadgets, calculators, audio gear, and electronics."),
            ("Textbooks & Study Guides", "books", "Core semester textbooks, reference guides, and solutions."),
            ("Academic Notes & PDFs", "notes", "Curated handwritten lecture notes, formula sheets, and study PDFs."),
            ("Bicycles & Mobility", "mobility", "Campus bicycles, mountain bikes, helmets, locks, and scooters."),
            ("Hostel & Room Essentials", "hostel", "Desks, lamps, fans, kettles, organizers, and dorm supplies."),
            ("Lab Gear & Instruments", "lab-gear", "Microcontrollers, lab coats, multimeter, soldering kits, and lab tools."),
        ]

        categories = {}
        for name, slug, desc in category_specs:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": desc, "is_active": True}
            )
            cat.name = name
            cat.is_active = True
            cat.save()
            categories[slug] = cat

        # 2. Ensure default sellers exist
        sellers = list(User.objects.filter(is_active=True))
        if not sellers:
            default_user = User.objects.create_user(
                username="campus_student",
                email="student@campus.edu",
                password="password123",
                institution="Engineering & Science Faculty"
            )
            sellers = [default_user]

        def get_seller(idx):
            return sellers[idx % len(sellers)]

        # Helper to generate or prepare image variations
        def prepare_image(target_name, base_filename, crop_box=None, brightness=1.0, contrast=1.0, color=1.0):
            target_path = os.path.join(media_images_dir, target_name)
            base_path = os.path.join(static_products_dir, base_filename)
            if not os.path.exists(base_path):
                alt_base = os.path.join(static_market_dir, base_filename)
                if os.path.exists(alt_base):
                    base_path = alt_base

            if not os.path.exists(base_path):
                # Fallback to any existing image
                for fallback in ["macbook-pro.jpg", "calculus-textbook.jpg", "campus-bicycle.jpg"]:
                    fb_path = os.path.join(static_products_dir, fallback)
                    if os.path.exists(fb_path):
                        base_path = fb_path
                        break

            try:
                with Image.open(base_path) as img:
                    img = img.convert("RGB")
                    w, h = img.size

                    if crop_box:
                        x1 = int(crop_box[0] * w)
                        y1 = int(crop_box[1] * h)
                        x2 = int(crop_box[2] * w)
                        y2 = int(crop_box[3] * h)
                        img = img.crop((x1, y1, x2, y2))

                    # Target standard aspect ratio 4:3 (800x600)
                    img = img.resize((800, 600), Image.Resampling.LANCZOS)

                    if brightness != 1.0:
                        img = ImageEnhance.Brightness(img).enhance(brightness)
                    if contrast != 1.0:
                        img = ImageEnhance.Contrast(img).enhance(contrast)
                    if color != 1.0:
                        img = ImageEnhance.Color(img).enhance(color)

                    img.save(target_path, "JPEG", quality=90)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not process {base_filename}: {e}"))

            return f"listings/images/{target_name}"

        # 3. Fix existing listings missing files
        self.stdout.write("Fixing images for existing listings...")
        fix_map = {
            1: ("macbook.jpg", "macbook-pro.jpg", (0.0, 0.0, 1.0, 1.0)),
            2: ("calculus.jpg", "calculus-textbook.jpg", (0.0, 0.1, 1.0, 0.9)),
            3: ("dsa_notes.jpg", "handwritten-notes.jpg", (0.0, 0.0, 1.0, 1.0)),
            4: ("casio_calculator.jpg", "scientific-calculator.jpg", (0.05, 0.05, 0.95, 0.95)),
            5: ("ipad_air.jpg", "ipad-air.jpg", (0.0, 0.0, 1.0, 1.0)),
            6: ("chemistry_mechanisms.jpg", "chemistry-book.jpg", (0.0, 0.1, 1.0, 0.9)),
            7: ("hero_honda.jpg", "campus-bicycle.jpg", (0.0, 0.0, 1.0, 1.0)),
        }

        for listing_id, (target_img, base_img, cbox) in fix_map.items():
            listing = Listing.objects.filter(id=listing_id).first()
            if listing:
                rel_path = prepare_image(target_img, base_img, crop_box=cbox)
                img_obj = listing.images.first()
                if not img_obj:
                    ListingImage.objects.create(
                        listing=listing,
                        image=rel_path,
                        is_primary=True,
                        alt_text=listing.title
                    )
                else:
                    if not img_obj.image or not os.path.exists(img_obj.image.path):
                        img_obj.image = rel_path
                        img_obj.is_primary = True
                        img_obj.save()

        # 4. Catalog Specification - ensuring at least 6 products in each category
        product_catalog = [
            # ================= Laptops & Electronics =================
            {
                "category": "laptops",
                "title": "Dell XPS 13 9310 (i7, 16GB RAM, 512GB SSD)",
                "slug": "dell-xps-13-9310-student-edition",
                "description": "Ultra-portable student laptop with 4K InfinityEdge touchscreen, 92% battery health, original 45W Type-C charger, and padded sleeve. Excellent for coding, simulations, and heavy multitasking.",
                "price": Decimal("52000.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Tech Block 3 / Library Quad",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "dell_xps_13.jpg",
                "base_image": "macbook-pro.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
                "brightness": 1.05,
                "contrast": 1.1,
                "color": 0.9,
            },
            {
                "category": "laptops",
                "title": "Lenovo ThinkPad T480 (Core i5, 16GB, Dual Battery)",
                "slug": "lenovo-thinkpad-t480-workstation",
                "description": "Legendary ThinkPad ergonomics with hot-swappable dual battery system providing up to 9 hours of real battery life. Pre-configured with Ubuntu 22.04 LTS and VS Code. Ideal for CS students.",
                "price": Decimal("28500.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "North Quad Computer Lab",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "thinkpad_t480.jpg",
                "base_image": "macbook-pro.jpg",
                "crop": (0.1, 0.05, 0.9, 0.95),
                "brightness": 0.92,
                "contrast": 1.15,
                "color": 0.75,
            },
            {
                "category": "laptops",
                "title": "Sony WH-1000XM4 Noise Cancelling Wireless Headphones",
                "slug": "sony-wh-1000xm4-anc-headphones",
                "description": "Top-tier active noise cancellation headphones for library study and late-night focus in the hostel. 30 hours battery backup, quick charge, includes original 3.5mm cable and travel carry case.",
                "price": Decimal("14500.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Central Library 2nd Floor",
                "is_negotiable": False,
                "is_urgent": True,
                "image_name": "sony_wh1000xm4.jpg",
                "base_image": "ipad-air.jpg",
                "crop": (0.15, 0.1, 0.85, 0.9),
                "brightness": 1.02,
                "contrast": 1.08,
                "color": 1.05,
            },
            {
                "category": "laptops",
                "title": "MacBook Pro M1 (16GB, 512GB Space Gray)",
                "slug": "macbook-pro-m1-campus-edition",
                "description": "Blazing fast M1 processor with 16GB unified memory. Flawless keyboard and retina display, 91% battery health, ideal for mobile app and web development.",
                "price": Decimal("58000.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "North Quad / Tech Block",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "macbook_pro_m1.jpg",
                "base_image": "macbook-pro.jpg",
                "crop": (0.0, 0.0, 1.0, 1.0),
            },
            {
                "category": "laptops",
                "title": "Casio FX-991EX ClassWiz Scientific Calculator",
                "slug": "casio-fx991ex-classwiz-calculator",
                "description": "Official exam approved non-programmable scientific calculator with high-resolution spreadsheet capabilities, QR code function, and dual solar/battery power.",
                "price": Decimal("850.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Engineering Quad",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "casio_fx991ex.jpg",
                "base_image": "scientific-calculator.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
            },
            {
                "category": "laptops",
                "title": "iPad Air 5th Gen (64GB Wi-Fi with Apple Pencil Support)",
                "slug": "ipad-air-5th-gen-space-gray",
                "description": "Apple M1 silicon with liquid retina display. Includes magnetic protective folio case, screen protector, and original 20W charger. Perfect for digital notes and paperless studying.",
                "price": Decimal("38500.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Main Campus Hostels",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "ipad_air_5th.jpg",
                "base_image": "ipad-air.jpg",
                "crop": (0.0, 0.0, 1.0, 1.0),
            },

            # ================= Textbooks & Study Guides =================
            {
                "category": "books",
                "title": "Calculus: Early Transcendentals (8th Ed. by Stewart)",
                "slug": "calculus-early-transcendentals-stewart",
                "description": "Standard Stewart Calculus textbook for 1st-year university mathematics. All formula inserts, chapter problem sets, and vector calculus guides intact.",
                "price": Decimal("450.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Central Library",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "calculus_stewart.jpg",
                "base_image": "calculus-textbook.jpg",
                "crop": (0.0, 0.1, 1.0, 0.9),
            },
            {
                "category": "books",
                "title": "Organic Chemistry: Principles & Mechanisms (Karthekeyan)",
                "slug": "organic-chemistry-principles-mechanisms-book",
                "description": "Thorough reaction mechanisms, stereochemistry walkthroughs, and spectroscopy problem sheets for chemistry & bioengineering students.",
                "price": Decimal("520.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Science Block A",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "organic_chem_book.jpg",
                "base_image": "chemistry-book.jpg",
                "crop": (0.0, 0.05, 1.0, 0.95),
            },
            {
                "category": "books",
                "title": "Discrete Mathematics and Its Applications (Kenneth Rosen)",
                "slug": "discrete-mathematics-applications-rosen",
                "description": "Standard theoretical computer science reference covering set theory, combinatorics, graph theory, propositional logic, and recurrence relations.",
                "price": Decimal("480.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Maths Dept Reading Room",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "discrete_math_rosen.jpg",
                "base_image": "calculus-textbook.jpg",
                "crop": (0.1, 0.05, 0.9, 0.95),
            },
            {
                "category": "books",
                "title": "Introduction to Algorithms (CLRS 4th Edition)",
                "slug": "clrs-introduction-to-algorithms-4th-ed",
                "description": "The definitive CS algorithm bible. Pristine condition with unblemished pages, zero highlighter marks, covering dynamic programming, graph algorithms, and NP-completeness.",
                "price": Decimal("850.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Department of Computer Science",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "clrs_algorithms.jpg",
                "base_image": "calculus-textbook.jpg",
                "crop": (0.05, 0.15, 0.95, 0.85),
                "brightness": 1.05,
                "contrast": 1.1,
                "color": 1.1,
            },
            {
                "category": "books",
                "title": "Computer Networking: A Top-Down Approach (Kurose & Ross 8th Ed.)",
                "slug": "computer-networking-top-down-approach-8th",
                "description": "Prescribed textbook for Computer Networks course. Comprehensive explanation of TCP/IP, Wireshark lab assignments, socket programming examples, and summary review sheets included.",
                "price": Decimal("620.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Central Library / Quad A",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "networking_kurose.jpg",
                "base_image": "chemistry-book.jpg",
                "crop": (0.05, 0.1, 0.95, 0.9),
                "brightness": 1.08,
                "contrast": 1.05,
                "color": 1.2,
            },
            {
                "category": "books",
                "title": "Engineering Mechanics: Statics & Dynamics (Hibbeler 14th Ed.)",
                "slug": "engineering-mechanics-statics-dynamics-hibbeler",
                "description": "Core textbook for 1st & 2nd year Mechanical, Civil, and Aerospace branches. Includes illustrated free-body diagrams, step-by-step problem sets, and vector moment derivations.",
                "price": Decimal("540.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Mechanical Engineering Dept",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "hibbeler_mechanics.jpg",
                "base_image": "civil-engineering-1.jpg",
                "crop": (0.0, 0.05, 1.0, 0.95),
                "brightness": 1.02,
                "contrast": 1.05,
                "color": 0.95,
            },

            # ================= Academic Notes & PDFs =================
            {
                "category": "notes",
                "title": "Operating Systems Exam Revision Notes & Formula Book",
                "slug": "os-exam-revision-notes-formula-book",
                "description": "High-yield handwritten summary notes on CPU scheduling algorithms, deadlock Banker's algorithm, virtual memory paging/TLB, and IPC semaphore implementations with clean diagrams.",
                "price": Decimal("180.00"),
                "listing_type": Listing.ListingType.DIGITAL,
                "condition": Listing.Condition.NEW,
                "location": "CS Department Common Room",
                "is_negotiable": False,
                "is_urgent": True,
                "image_name": "os_notes.jpg",
                "base_image": "handwritten-notes.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
                "brightness": 1.08,
                "contrast": 1.12,
                "color": 1.05,
            },
            {
                "category": "notes",
                "title": "Computer Architecture & 8086 Assembly Cheatsheet",
                "slug": "computer-architecture-8086-cheatsheet",
                "description": "Color-coded revision tables for instruction pipelining, cache memory hit-rate formulas, RISC vs CISC comparisons, and 8086 timing state diagrams for end-semester examinations.",
                "price": Decimal("140.00"),
                "listing_type": Listing.ListingType.DIGITAL,
                "condition": Listing.Condition.NEW,
                "location": "Tech Quad Block A",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "co_architecture_notes.jpg",
                "base_image": "handwritten-notes.jpg",
                "crop": (0.1, 0.0, 0.9, 0.9),
                "brightness": 1.02,
                "contrast": 1.18,
                "color": 0.95,
            },
            {
                "category": "notes",
                "title": "Engineering Mathematics III (Transforms & PDE) Complete Guide",
                "slug": "engg-math-3-transforms-pde-guide",
                "description": "Step-by-step solved past 5 years university question papers for Fourier Series, Laplace Transforms, Z-Transforms, and Partial Differential Equations with formula cheat sheets.",
                "price": Decimal("220.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Main Library Reading Hall",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "math3_notes.jpg",
                "base_image": "handwritten-notes.jpg",
                "crop": (0.0, 0.1, 1.0, 1.0),
                "brightness": 1.12,
                "contrast": 1.08,
                "color": 1.1,
            },
            {
                "category": "notes",
                "title": "Database Management Systems (DBMS) Quick Review Notes",
                "slug": "dbms-quick-review-notes-sql-normalization",
                "description": "Condensed notes covering relational algebra, B+ Tree indexing, 3NF/BCNF normalization algorithms, ACID properties, and transaction concurrency recovery protocols.",
                "price": Decimal("160.00"),
                "listing_type": Listing.ListingType.DIGITAL,
                "condition": Listing.Condition.NEW,
                "location": "IT Block 2nd Floor",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "dbms_review_notes.jpg",
                "base_image": "handwritten-notes.jpg",
                "crop": (0.05, 0.15, 0.95, 0.95),
                "brightness": 1.04,
                "contrast": 1.1,
                "color": 1.0,
            },
            {
                "category": "notes",
                "title": "Machine Learning & Deep Learning Interview Preparation Sheets",
                "slug": "ml-dl-interview-preparation-sheets",
                "description": "Formula reference and architectural intuition diagrams for Gradient Descent, Convolutional Neural Networks, Transformer attention mechanisms, and model evaluation metrics.",
                "price": Decimal("200.00"),
                "listing_type": Listing.ListingType.DIGITAL,
                "condition": Listing.Condition.NEW,
                "location": "AI/ML Lab Tech Park",
                "is_negotiable": False,
                "is_urgent": True,
                "image_name": "ml_interview_sheets.jpg",
                "base_image": "handwritten-notes.jpg",
                "crop": (0.1, 0.1, 0.9, 0.9),
                "brightness": 1.1,
                "contrast": 1.15,
                "color": 1.15,
            },
            {
                "category": "notes",
                "title": "Data Structures & Algorithms Comprehensive Revision Notes",
                "slug": "dsa-comprehensive-revision-notes-sheet",
                "description": "Exhaustive handwritten notes on Arrays, Linked Lists, Stacks, Queues, Binary Trees, AVL Trees, Heaps, and Dynamic Programming with color-coded diagrams.",
                "price": Decimal("150.00"),
                "listing_type": Listing.ListingType.DIGITAL,
                "condition": Listing.Condition.NEW,
                "location": "Academic Block B",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "dsa_comprehensive_notes.jpg",
                "base_image": "handwritten-notes.jpg",
                "crop": (0.0, 0.0, 1.0, 1.0),
            },

            # ================= Bicycles & Mobility =================
            {
                "category": "mobility",
                "title": "Firefox Target 21-Speed Mountain Bike (27.5T)",
                "slug": "firefox-target-21-speed-mountain-bike",
                "description": "Lightweight alloy hardtail MTB with Shimano Tourney 21-speed gearing and dual disc brakes. Recently serviced cables, smooth chain, includes strong numbered cable lock and mudguards.",
                "price": Decimal("7500.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "South Hostel Parking Stand",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "firefox_target_mtb.jpg",
                "base_image": "campus-bicycle.jpg",
                "crop": (0.0, 0.05, 1.0, 0.95),
                "brightness": 1.05,
                "contrast": 1.12,
                "color": 1.15,
            },
            {
                "category": "mobility",
                "title": "Hero Sprint Pro Single Speed Campus Commuter",
                "slug": "hero-sprint-pro-single-speed-commuter",
                "description": "Super reliable, zero-maintenance single speed bicycle with brand new tires and comfortable foam saddle. Includes front wire basket for college bags and rear LED warning light.",
                "price": Decimal("3800.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Engineering Quad Bicycle Bay",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "hero_sprint_commuter.jpg",
                "base_image": "campus-bicycle.jpg",
                "crop": (0.05, 0.0, 0.95, 0.9),
                "brightness": 0.98,
                "contrast": 1.08,
                "color": 1.0,
            },
            {
                "category": "mobility",
                "title": "Hercules Roadeo A50 Hardtail Bike (Front Suspension)",
                "slug": "hercules-roadeo-a50-hardtail-bike",
                "description": "Tough student bicycle with responsive front suspension to tackle campus potholes. Quick-release seat post for easy height adjustment between peer roommates.",
                "price": Decimal("5200.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.FAIR,
                "location": "Hostel 8 Cycle Shed",
                "is_negotiable": True,
                "is_urgent": True,
                "image_name": "hercules_roadeo_a50.jpg",
                "base_image": "campus-bicycle.jpg",
                "crop": (0.1, 0.05, 0.9, 0.95),
                "brightness": 1.02,
                "contrast": 1.2,
                "color": 0.9,
            },
            {
                "category": "mobility",
                "title": "Btwin Riverside 120 Hybrid Cycle (8-Speed)",
                "slug": "btwin-riverside-120-hybrid-cycle",
                "description": "Ergonomic hybrid frame with 700c smooth rolling tires and Microshift 8-speed thumb shifters. Ideal for daily commuting between departments and hostel campus mess.",
                "price": Decimal("8200.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Student Activity Centre",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "btwin_riverside_120.jpg",
                "base_image": "campus-bicycle.jpg",
                "crop": (0.0, 0.1, 1.0, 1.0),
                "brightness": 1.08,
                "contrast": 1.05,
                "color": 1.2,
            },
            {
                "category": "mobility",
                "title": "Decathlon Rockrider ST30 Mountain Bike (Daily/Sem Rental)",
                "slug": "decathlon-rockrider-st30-campus-rental",
                "description": "Available for daily or semester-long campus rental. Rigid fork, V-brakes, tuned gear changes, helmet, and anti-theft U-lock provided. Perfect for semester exchange students.",
                "price": Decimal("120.00"),
                "listing_type": Listing.ListingType.RENT,
                "rental_period": Listing.RentalPeriod.DAY,
                "condition": Listing.Condition.GOOD,
                "location": "Sports Complex Pavilion",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "rockrider_st30_rental.jpg",
                "base_image": "campus-bicycle.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
                "brightness": 1.1,
                "contrast": 1.1,
                "color": 1.05,
            },
            {
                "category": "mobility",
                "title": "Hero Honda Street Commuter Bike (Serviced & Ready)",
                "slug": "hero-honda-street-commuter-campus",
                "description": "Smooth running commuter motorcycle in good working order. Serviced last month with new spark plugs and clean chain. Registered campus parking pass included.",
                "price": Decimal("2000.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Campus Main Parking",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "hero_honda_commuter.jpg",
                "base_image": "campus-bicycle.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
            },

            # ================= Hostel & Room Essentials =================
            {
                "category": "hostel",
                "title": "LED Dual-Mode Study Desk Lamp with USB Fast Charger",
                "slug": "led-dual-mode-study-desk-lamp",
                "description": "3 color temperature modes (Warm, Natural, Cool White) with capacitive touch dimming and a 5V USB output port to charge your phone or headphones right from the lamp base.",
                "price": Decimal("650.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Hostel 3 Block B",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "led_study_lamp.jpg",
                "base_image": "dorm-desk-lamp.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
                "brightness": 1.05,
                "contrast": 1.08,
                "color": 1.1,
            },
            {
                "category": "hostel",
                "title": "Foldable Ergonomic Study Table with Cup & Tablet Holder",
                "slug": "foldable-ergonomic-study-table",
                "description": "Compact bed and floor study desk featuring non-slip curved legs, tablet viewing slot, and dedicated cup holder. Folds flat in 2 seconds to tuck cleanly under your hostel bed.",
                "price": Decimal("580.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Hostel 5 Room 214",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "foldable_study_table.jpg",
                "base_image": "study-desk.jpg",
                "crop": (0.0, 0.05, 1.0, 0.95),
                "brightness": 1.08,
                "contrast": 1.05,
                "color": 1.0,
            },
            {
                "category": "hostel",
                "title": "High-Back Ergonomic Mesh Desk Chair with Lumbar Support",
                "slug": "high-back-ergonomic-mesh-chair",
                "description": "Breathable high-back mesh design with adjustable lumbar support, pneumatic gas-lift seat adjustment, and smooth-gliding nylon casters. Protects posture during long study sessions.",
                "price": Decimal("3200.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "PG Hostel Block C",
                "is_negotiable": True,
                "is_urgent": True,
                "image_name": "ergonomic_mesh_chair.jpg",
                "base_image": "study-desk.jpg",
                "crop": (0.1, 0.1, 0.9, 0.9),
                "brightness": 0.95,
                "contrast": 1.15,
                "color": 0.9,
            },
            {
                "category": "hostel",
                "title": "Pigeon 1.5L Stainless Steel Electric Kettle (1500W)",
                "slug": "pigeon-1-5l-stainless-steel-electric-kettle",
                "description": "Boils water within 3 minutes with automatic shut-off and boil-dry protection. 360-degree cordless swivel base. Essential companion for late-night coffee, tea, and hostel ramen.",
                "price": Decimal("480.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Hostel Mess 1 Lobby",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "electric_kettle.jpg",
                "base_image": "dorm-desk-lamp.jpg",
                "crop": (0.15, 0.1, 0.85, 0.9),
                "brightness": 1.1,
                "contrast": 1.05,
                "color": 0.95,
            },
            {
                "category": "hostel",
                "title": "4-Tier Collapsible Shoe & Book Organizer Rack",
                "slug": "4-tier-collapsible-shoe-book-rack",
                "description": "Durable steel tube and non-woven fabric organizer rack. Holds up to 12 pairs of shoes, books, or folded laundry. Completely tool-free assembly, ideal for small shared hostel rooms.",
                "price": Decimal("350.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Hostel 2 First Floor",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "shoe_book_rack.jpg",
                "base_image": "study-desk.jpg",
                "crop": (0.05, 0.15, 0.95, 0.85),
                "brightness": 1.02,
                "contrast": 1.1,
                "color": 1.05,
            },
            {
                "category": "hostel",
                "title": "Rechargeable USB High-Speed Table Fan (4000mAh Battery)",
                "slug": "rechargeable-usb-table-fan-4000mah",
                "description": "Ultra-quiet brushless motor with 3 speed settings and 120-degree tilt. Integrated 4000mAh battery provides up to 8 hours of cooling backup during campus power outages.",
                "price": Decimal("750.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Hostel 7 Common Room",
                "is_negotiable": False,
                "is_urgent": True,
                "image_name": "rechargeable_fan.jpg",
                "base_image": "dorm-desk-lamp.jpg",
                "crop": (0.1, 0.05, 0.9, 0.95),
                "brightness": 1.0,
                "contrast": 1.12,
                "color": 1.2,
            },

            # ================= Lab Gear & Instruments =================
            {
                "category": "lab-gear",
                "title": "Arduino Mega 2560 Starter Lab Kit with 35+ Modules",
                "slug": "arduino-mega-2560-starter-lab-kit",
                "description": "Complete embedded systems project kit including Arduino Mega board, RFID sensor, ultrasonic HC-SR04, servo motor, relay modules, 830-point breadboard, and 65 jumper wires.",
                "price": Decimal("1850.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Robotics & Automation Lab",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "arduino_mega_kit.jpg",
                "base_image": "lab-kit.jpg",
                "crop": (0.0, 0.0, 1.0, 1.0),
                "brightness": 1.05,
                "contrast": 1.1,
                "color": 1.1,
            },
            {
                "category": "lab-gear",
                "title": "Mastech MAS830L Digital Multimeter with Probes",
                "slug": "mastech-mas830l-digital-multimeter",
                "description": "Handheld digital multimeter measuring AC/DC voltage, current, resistance, continuity buzzer, and hFE transistor tester. Backlit display with protective rubber holster.",
                "price": Decimal("450.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.GOOD,
                "location": "Electrical Sciences Lab",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "mastech_multimeter.jpg",
                "base_image": "scientific-calculator.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
                "brightness": 0.98,
                "contrast": 1.15,
                "color": 0.9,
            },
            {
                "category": "lab-gear",
                "title": "100% Cotton Pure White Lab Coat & UV Safety Goggles",
                "slug": "cotton-lab-coat-uv-safety-goggles",
                "description": "Standard university compliant cotton lab coat (Size L / 40) with 3 deep pockets and clear polycarbonate anti-fog safety goggles. Mandatory for Chemistry & Biotech lab sessions.",
                "price": Decimal("380.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "Science Block Chemistry Lab",
                "is_negotiable": False,
                "is_urgent": True,
                "image_name": "lab_coat_goggles.jpg",
                "base_image": "lab-kit.jpg",
                "crop": (0.1, 0.1, 0.9, 0.9),
                "brightness": 1.15,
                "contrast": 1.05,
                "color": 0.85,
            },
            {
                "category": "lab-gear",
                "title": "Temperature Controlled Soldering Iron Kit (60W) with Stand",
                "slug": "temperature-controlled-soldering-iron-kit",
                "description": "Adjustable temperature dial (200°C - 450°C), heat-insulated silicone handle, 5 interchangeable tips, desoldering pump, tweezers, cleaning sponge, and lead-free rosin core solder.",
                "price": Decimal("720.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "MakerSpace Workshop",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "soldering_iron_kit.jpg",
                "base_image": "lab-kit.jpg",
                "crop": (0.05, 0.05, 0.95, 0.95),
                "brightness": 1.02,
                "contrast": 1.18,
                "color": 1.05,
            },
            {
                "category": "lab-gear",
                "title": "Raspberry Pi 4 Model B (4GB RAM) with Official Case & Fan",
                "slug": "raspberry-pi-4-model-b-4gb-case",
                "description": "Broadcom BCM2711 quad-core 64-bit microcomputer with 4GB LPDDR4, dual Micro-HDMI 4K outputs, 32GB Class 10 MicroSD pre-installed with Raspberry Pi OS, and official 15W USB-C PSU.",
                "price": Decimal("5800.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.LIKE_NEW,
                "location": "IoT & Embedded Systems Lab",
                "is_negotiable": True,
                "is_urgent": False,
                "image_name": "raspberry_pi_4.jpg",
                "base_image": "lab-kit.jpg",
                "crop": (0.15, 0.05, 0.85, 0.95),
                "brightness": 1.08,
                "contrast": 1.1,
                "color": 1.25,
            },
            {
                "category": "lab-gear",
                "title": "Electronic Component Assortment Box (Resistors, Capacitors, ICs)",
                "slug": "electronic-component-assortment-box-600pcs",
                "description": "Organized 24-compartment storage box containing 600+ 1/4W 1% metal film resistors (30 values), ceramic capacitors, 555 timers, LM358 op-amps, and assorted 5mm bright LEDs.",
                "price": Decimal("390.00"),
                "listing_type": Listing.ListingType.SALE,
                "condition": Listing.Condition.NEW,
                "location": "Electronics Dept Store",
                "is_negotiable": False,
                "is_urgent": False,
                "image_name": "components_assortment_box.jpg",
                "base_image": "lab-kit.jpg",
                "crop": (0.05, 0.15, 0.95, 0.85),
                "brightness": 0.98,
                "contrast": 1.12,
                "color": 1.0,
            },
        ]

        created_count = 0
        updated_count = 0

        for idx, item in enumerate(product_catalog):
            cat = categories.get(item["category"])
            if not cat:
                continue

            rel_img = prepare_image(
                item["image_name"],
                item["base_image"],
                crop_box=item.get("crop"),
                brightness=item.get("brightness", 1.0),
                contrast=item.get("contrast", 1.0),
                color=item.get("color", 1.0)
            )

            seller = get_seller(idx)

            listing, created = Listing.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "seller": seller,
                    "category": cat,
                    "title": item["title"],
                    "description": item["description"],
                    "price": item["price"],
                    "listing_type": item["listing_type"],
                    "condition": item["condition"],
                    "rental_period": item.get("rental_period", ""),
                    "location": item["location"],
                    "is_negotiable": item.get("is_negotiable", False),
                    "is_urgent": item.get("is_urgent", False),
                    "status": Listing.ListingStatus.ACTIVE,
                }
            )

            if not created:
                # Update details and category
                listing.category = cat
                listing.title = item["title"]
                listing.description = item["description"]
                listing.price = item["price"]
                listing.listing_type = item["listing_type"]
                listing.condition = item["condition"]
                listing.location = item["location"]
                listing.status = Listing.ListingStatus.ACTIVE
                listing.save()
                updated_count += 1
            else:
                created_count += 1

            # Ensure listing image
            listing_img = listing.images.filter(is_primary=True).first() or listing.images.first()
            if not listing_img:
                ListingImage.objects.create(
                    listing=listing,
                    image=rel_img,
                    is_primary=True,
                    alt_text=item["title"]
                )
            else:
                listing_img.image = rel_img
                listing_img.is_primary = True
                listing_img.alt_text = item["title"]
                listing_img.save()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded marketplace! Created: {created_count}, Updated: {updated_count}."
        ))

        # Output final breakdown per category
        self.stdout.write("\nFinal category listing counts:")
        for cat in Category.objects.filter(is_active=True):
            active_count = cat.listings.filter(status=Listing.ListingStatus.ACTIVE).count()
            self.stdout.write(f" - {cat.name} ({cat.slug}): {active_count} active listings")
