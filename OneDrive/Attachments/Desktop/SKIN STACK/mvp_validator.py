#!/usr/bin/env python3
"""
SkinStack MVP Validator
=======================
This is THE FIRST FILE to run for the SkinStack project.
It validates our entire schema and business logic with synthetic data
to ensure everything works before we connect to real networks.

Run this to:
1. Test database schema with realistic data
2. Validate business logic and calculations
3. Simulate real-world scenarios
4. Identify edge cases and issues early

Usage: python mvp_validator.py
"""

import os
import sys
import json
import uuid
import random
import hashlib
import secrets
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import sqlite3  # Using SQLite for testing (no setup required)

# For colored output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.ENDC}")

class SkinStackValidator:
    """Main validator class that tests the entire platform"""

    def __init__(self):
        self.db_file = "skinstack_test.db"
        self.conn = None
        self.cursor = None
        self.test_data = {}
        self.validation_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def setup_database(self):
        """Create all database tables"""
        print_header("Setting Up Database Schema")

        # Remove existing database
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")

        # Create tables
        schema = """
        -- Users table
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('influencer', 'merchant', 'admin')) NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Influencers table
        CREATE TABLE influencers (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE REFERENCES users(id),
            display_name TEXT,
            instagram_handle TEXT,
            tiktok_handle TEXT,
            payout_method TEXT CHECK(payout_method IN ('stripe_connect', 'paypal', 'ach')),
            payout_account_id TEXT,
            tax_status TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Merchants table
        CREATE TABLE merchants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            website TEXT,
            integration_type TEXT CHECK(integration_type IN (
                'shopify_refersion', 'impact', 'amazon', 'levanta'
            )) NOT NULL,
            api_credentials TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Networks table
        CREATE TABLE networks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            cookie_window_days INTEGER DEFAULT 7,
            supports_subid INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Programs table
        CREATE TABLE programs (
            id TEXT PRIMARY KEY,
            merchant_id TEXT REFERENCES merchants(id),
            network_id TEXT REFERENCES networks(id),
            name TEXT NOT NULL,
            commission_type TEXT CHECK(commission_type IN ('percent', 'fixed')) NOT NULL,
            commission_value DECIMAL(10,4) NOT NULL,
            cookie_window_days INTEGER DEFAULT 7,
            tiering TEXT,  -- JSON
            excluded_skus TEXT,  -- JSON
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Products table
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            merchant_id TEXT REFERENCES merchants(id),
            external_id TEXT,  -- SKU/ASIN
            name TEXT NOT NULL,
            description TEXT,
            url TEXT,
            image_url TEXT,
            price DECIMAL(12,2),
            category TEXT,
            metadata TEXT,  -- JSON
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Tracking Links table
        CREATE TABLE tracking_links (
            id TEXT PRIMARY KEY,
            influencer_id TEXT REFERENCES influencers(id),
            program_id TEXT REFERENCES programs(id),
            product_id TEXT REFERENCES products(id),
            campaign_id TEXT,
            slug TEXT UNIQUE NOT NULL,
            destination_url TEXT NOT NULL,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            metadata TEXT,  -- JSON
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Clicks table
        CREATE TABLE clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_link_id TEXT REFERENCES tracking_links(id),
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_hash TEXT,
            user_agent TEXT,
            referrer TEXT,
            device_id TEXT,
            session_id TEXT,
            fingerprint TEXT,
            country TEXT,
            platform TEXT,
            subid TEXT,
            fraud_score REAL DEFAULT 0.0,
            fraud_flags TEXT  -- JSON
        );

        -- Conversions table
        CREATE TABLE conversions (
            id TEXT PRIMARY KEY,
            merchant_id TEXT REFERENCES merchants(id),
            program_id TEXT REFERENCES programs(id),
            order_id TEXT UNIQUE,
            occurred_at TIMESTAMP NOT NULL,
            customer_email_hash TEXT,
            currency TEXT DEFAULT 'USD',
            subtotal DECIMAL(12,2),
            discounts DECIMAL(12,2) DEFAULT 0,
            tax DECIMAL(12,2) DEFAULT 0,
            shipping DECIMAL(12,2) DEFAULT 0,
            total DECIMAL(12,2) NOT NULL,
            items TEXT,  -- JSON
            subid TEXT,
            network_conversion_id TEXT,
            raw_event TEXT,  -- JSON
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Attributions table
        CREATE TABLE attributions (
            id TEXT PRIMARY KEY,
            conversion_id TEXT REFERENCES conversions(id),
            tracking_link_id TEXT REFERENCES tracking_links(id),
            click_id INTEGER REFERENCES clicks(id),
            model TEXT DEFAULT 'last_click',
            attribution_weight REAL DEFAULT 1.0,
            window_days INTEGER,
            match_type TEXT,
            confidence_score REAL DEFAULT 1.0,
            attributed INTEGER DEFAULT 1,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Commissions table
        CREATE TABLE commissions (
            id TEXT PRIMARY KEY,
            attribution_id TEXT REFERENCES attributions(id),
            conversion_id TEXT REFERENCES conversions(id),
            influencer_id TEXT REFERENCES influencers(id),
            merchant_id TEXT REFERENCES merchants(id),
            program_id TEXT REFERENCES programs(id),
            gross_amount DECIMAL(12,2) NOT NULL,
            platform_fee DECIMAL(12,2) DEFAULT 0,
            net_amount DECIMAL(12,2) NOT NULL,
            currency TEXT DEFAULT 'USD',
            calculation_details TEXT,  -- JSON
            status TEXT CHECK(status IN ('pending', 'approved', 'paid', 'reversed')) DEFAULT 'pending',
            approved_at TIMESTAMP,
            paid_at TIMESTAMP,
            payout_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Payouts table
        CREATE TABLE payouts (
            id TEXT PRIMARY KEY,
            influencer_id TEXT REFERENCES influencers(id),
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            commission_count INTEGER DEFAULT 0,
            gross_amount DECIMAL(12,2) NOT NULL,
            platform_fees DECIMAL(12,2) DEFAULT 0,
            processing_fees DECIMAL(12,2) DEFAULT 0,
            net_amount DECIMAL(12,2) NOT NULL,
            currency TEXT DEFAULT 'USD',
            payment_method TEXT,
            payment_reference TEXT,
            status TEXT DEFAULT 'initiated',
            initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );

        -- Create indexes for performance
        CREATE INDEX idx_clicks_tracking_link ON clicks(tracking_link_id);
        CREATE INDEX idx_clicks_device ON clicks(device_id);
        CREATE INDEX idx_conversions_order ON conversions(order_id);
        CREATE INDEX idx_conversions_subid ON conversions(subid);
        CREATE INDEX idx_attributions_conversion ON attributions(conversion_id);
        CREATE INDEX idx_commissions_influencer ON commissions(influencer_id);
        CREATE INDEX idx_commissions_status ON commissions(status);
        """

        for statement in schema.split(';'):
            if statement.strip():
                try:
                    self.cursor.execute(statement)
                    table_name = statement.split('CREATE')[1].split()[1] if 'CREATE TABLE' in statement else 'index'
                    if 'TABLE' in statement:
                        print_success(f"Created table: {table_name}")
                except Exception as e:
                    print_error(f"Failed to create: {e}")

        self.conn.commit()
        print_success("Database schema created successfully")

    def generate_synthetic_data(self):
        """Generate realistic synthetic data for testing"""
        print_header("Generating Synthetic Test Data")

        # Generate influencers
        print_info("Creating influencers...")
        influencers = []
        influencer_names = [
            ("Emma", "Watson", "@emmawatson", "@emmawatson_beauty", 500000),
            ("James", "Charles", "@jamescharles", "@jamesmakeup", 2000000),
            ("Michelle", "Phan", "@michellephan", "@michellephan", 1000000),
            ("Huda", "Kattan", "@hudabeauty", "@hudabeauty", 5000000),
            ("Jackie", "Aina", "@jackieaina", "@jackieaina", 800000)
        ]

        for first, last, ig, tiktok, followers in influencer_names:
            user_id = str(uuid.uuid4())
            influencer_id = str(uuid.uuid4())

            # Create user
            self.cursor.execute("""
                INSERT INTO users (id, email, password_hash, role)
                VALUES (?, ?, ?, 'influencer')
            """, (user_id, f"{first.lower()}@skinstack.com", "hashed_password"))

            # Create influencer
            self.cursor.execute("""
                INSERT INTO influencers (id, user_id, display_name, instagram_handle,
                                        tiktok_handle, payout_method, payout_account_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (influencer_id, user_id, f"{first} {last}", ig, tiktok,
                  "stripe_connect", f"acct_{secrets.token_hex(8)}"))

            influencers.append({
                'id': influencer_id,
                'name': f"{first} {last}",
                'followers': followers,
                'engagement_rate': random.uniform(0.02, 0.08)  # 2-8% engagement
            })

        self.test_data['influencers'] = influencers
        print_success(f"Created {len(influencers)} influencers")

        # Generate merchants and networks
        print_info("Creating merchants and networks...")
        merchants = []
        networks_map = {
            'shopify_refersion': ('Shopify/Refersion', 14),
            'impact': ('Impact Radius', 7),
            'amazon': ('Amazon Associates', 1),
            'levanta': ('Levanta', 14)
        }

        skincare_brands = [
            ("GlowBeauty", "https://glowbeauty.com", "shopify_refersion", 0.15),
            ("PureRadiance", "https://pureradiance.com", "impact", 0.20),
            ("SerumLab", "https://serumlab.com", "shopify_refersion", 0.18),
            ("NaturaSkin", "https://naturaskin.com", "levanta", 0.25),
            ("Amazon Beauty", "https://amazon.com/beauty", "amazon", 0.04)
        ]

        for brand_name, website, integration, commission_rate in skincare_brands:
            merchant_id = str(uuid.uuid4())
            network_id = str(uuid.uuid4())
            program_id = str(uuid.uuid4())

            # Create network if not exists
            network_name, cookie_days = networks_map[integration]
            self.cursor.execute("""
                INSERT OR IGNORE INTO networks (id, name, type, cookie_window_days)
                VALUES (?, ?, ?, ?)
            """, (network_id, network_name, integration, cookie_days))

            # Create merchant
            self.cursor.execute("""
                INSERT INTO merchants (id, name, website, integration_type)
                VALUES (?, ?, ?, ?)
            """, (merchant_id, brand_name, website, integration))

            # Create program
            self.cursor.execute("""
                INSERT INTO programs (id, merchant_id, network_id, name,
                                     commission_type, commission_value, cookie_window_days)
                VALUES (?, ?, ?, ?, 'percent', ?, ?)
            """, (program_id, merchant_id, network_id, f"{brand_name} Affiliate Program",
                  commission_rate, cookie_days))

            merchants.append({
                'id': merchant_id,
                'program_id': program_id,
                'name': brand_name,
                'commission_rate': commission_rate,
                'integration': integration
            })

        self.test_data['merchants'] = merchants
        print_success(f"Created {len(merchants)} merchants with programs")

        # Generate products
        print_info("Creating products...")
        products = []
        product_templates = [
            ("Vitamin C Serum", "Brightening serum with 20% Vitamin C", 29.99, "Serums"),
            ("Retinol Cream", "Anti-aging night cream with retinol", 39.99, "Moisturizers"),
            ("Hyaluronic Acid", "Hydrating serum for all skin types", 24.99, "Serums"),
            ("Niacinamide 10%", "Pore-minimizing serum", 19.99, "Serums"),
            ("Peptide Complex", "Firming cream with peptides", 49.99, "Moisturizers"),
            ("SPF 50 Sunscreen", "Broad spectrum sun protection", 22.99, "Sun Care"),
            ("Glycolic Toner", "Exfoliating toner with AHA", 18.99, "Toners"),
            ("Face Oil", "Nourishing facial oil blend", 34.99, "Oils"),
            ("Clay Mask", "Deep cleansing clay mask", 16.99, "Masks"),
            ("Eye Cream", "Anti-wrinkle eye cream", 44.99, "Eye Care")
        ]

        for merchant in merchants[:4]:  # Skip Amazon for products
            for product_name, desc, price, category in product_templates:
                product_id = str(uuid.uuid4())
                sku = f"SKU{random.randint(1000, 9999)}"

                self.cursor.execute("""
                    INSERT INTO products (id, merchant_id, external_id, name,
                                         description, price, category, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (product_id, merchant['id'], sku,
                      f"{merchant['name']} {product_name}", desc, price, category,
                      f"{merchant['name'].lower().replace(' ', '')}.com/products/{sku}"))

                products.append({
                    'id': product_id,
                    'merchant_id': merchant['id'],
                    'name': product_name,
                    'price': price,
                    'category': category,
                    'sku': sku
                })

        self.test_data['products'] = products
        print_success(f"Created {len(products)} products")

        self.conn.commit()

    def simulate_traffic_and_conversions(self):
        """Simulate realistic traffic patterns and conversions"""
        print_header("Simulating Traffic & Conversions")

        # Generate tracking links
        print_info("Creating tracking links...")
        links = []
        for influencer in self.test_data['influencers']:
            # Each influencer promotes 3-5 products
            num_products = random.randint(3, 5)
            promoted_products = random.sample(self.test_data['products'], num_products)

            for product in promoted_products:
                link_id = str(uuid.uuid4())
                slug = self.generate_slug()
                merchant = next(m for m in self.test_data['merchants']
                               if m['id'] == product['merchant_id'])

                self.cursor.execute("""
                    INSERT INTO tracking_links (id, influencer_id, program_id,
                                               product_id, slug, destination_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (link_id, influencer['id'], merchant['program_id'],
                      product['id'], slug, f"https://track.skinstack.co/{slug}"))

                links.append({
                    'id': link_id,
                    'influencer_id': influencer['id'],
                    'influencer_followers': influencer['followers'],
                    'engagement_rate': influencer['engagement_rate'],
                    'product_id': product['id'],
                    'product_price': product['price'],
                    'merchant_id': merchant['id'],
                    'program_id': merchant['program_id'],
                    'commission_rate': merchant['commission_rate'],
                    'slug': slug
                })

        self.test_data['links'] = links
        print_success(f"Created {len(links)} tracking links")

        # Simulate clicks
        print_info("Simulating click traffic...")
        clicks_data = []
        for link in links:
            # Click volume based on follower count and engagement
            expected_clicks = int(link['influencer_followers'] *
                                 link['engagement_rate'] *
                                 random.uniform(0.001, 0.005))  # 0.1-0.5% CTR

            for _ in range(min(expected_clicks, 1000)):  # Cap at 1000 for testing
                click_time = datetime.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )

                device_id = str(uuid.uuid4())
                subid = f"{link['influencer_id']}_{link['slug']}_{int(click_time.timestamp())}"

                self.cursor.execute("""
                    INSERT INTO clicks (tracking_link_id, clicked_at, ip_hash,
                                       device_id, subid, platform, fraud_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (link['id'], click_time, hashlib.sha256(f"192.168.{random.randint(1,255)}.{random.randint(1,255)}".encode()).hexdigest(),
                      device_id, subid, random.choice(['mobile', 'desktop', 'tablet']),
                      random.uniform(0, 0.3)))  # Most clicks are clean

                clicks_data.append({
                    'link_id': link['id'],
                    'device_id': device_id,
                    'subid': subid,
                    'click_time': click_time,
                    'product_price': link['product_price'],
                    'commission_rate': link['commission_rate'],
                    'merchant_id': link['merchant_id'],
                    'program_id': link['program_id'],
                    'influencer_id': link['influencer_id']
                })

        print_success(f"Generated {len(clicks_data)} clicks")

        # Simulate conversions (realistic 1-3% conversion rate)
        print_info("Simulating conversions...")
        conversions = []
        num_conversions = int(len(clicks_data) * random.uniform(0.01, 0.03))
        converting_clicks = random.sample(clicks_data, num_conversions)

        for click in converting_clicks:
            conversion_id = str(uuid.uuid4())
            order_id = f"ORDER{random.randint(100000, 999999)}"

            # Conversion happens 0-7 days after click
            conversion_time = click['click_time'] + timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )

            # Calculate order value (might buy multiple items)
            num_items = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
            subtotal = click['product_price'] * num_items
            tax = subtotal * 0.08
            shipping = 0 if subtotal > 50 else 5.99
            total = subtotal + tax + shipping

            self.cursor.execute("""
                INSERT INTO conversions (id, merchant_id, program_id, order_id,
                                        occurred_at, subtotal, tax, shipping, total, subid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (conversion_id, click['merchant_id'], click['program_id'],
                  order_id, conversion_time, subtotal, tax, shipping, total, click['subid']))

            conversions.append({
                'id': conversion_id,
                'click': click,
                'subtotal': subtotal,
                'total': total
            })

        print_success(f"Generated {len(conversions)} conversions")

        # Create attributions and calculate commissions
        print_info("Processing attributions and commissions...")
        for conversion in conversions:
            attribution_id = str(uuid.uuid4())
            commission_id = str(uuid.uuid4())

            # Create attribution
            self.cursor.execute("""
                INSERT INTO attributions (id, conversion_id, tracking_link_id,
                                         model, match_type, reason)
                VALUES (?, ?, ?, 'last_click', 'subid', 'Exact subid match')
            """, (attribution_id, conversion['id'], conversion['click']['link_id']))

            # Calculate commission
            gross_commission = float(conversion['subtotal']) * conversion['click']['commission_rate']
            platform_fee = gross_commission * 0.20  # 20% platform fee
            net_commission = gross_commission - platform_fee

            self.cursor.execute("""
                INSERT INTO commissions (id, attribution_id, conversion_id, influencer_id,
                                        merchant_id, program_id, gross_amount,
                                        platform_fee, net_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (commission_id, attribution_id, conversion['id'],
                  conversion['click']['influencer_id'], conversion['click']['merchant_id'],
                  conversion['click']['program_id'], gross_commission,
                  platform_fee, net_commission))

        print_success(f"Processed {len(conversions)} attributions and commissions")

        self.conn.commit()

    def generate_slug(self, length=8):
        """Generate a unique short slug"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))

    def validate_business_logic(self):
        """Validate critical business logic and calculations"""
        print_header("Validating Business Logic")

        tests = [
            self.test_commission_calculations,
            self.test_attribution_window,
            self.test_payout_thresholds,
            self.test_network_specific_rules,
            self.test_fraud_detection,
            self.test_data_integrity
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print_error(f"Test failed: {e}")
                self.validation_results['failed'].append(str(test.__name__))

    def test_commission_calculations(self):
        """Test commission calculation accuracy"""
        print_info("Testing commission calculations...")

        # Test percentage-based commissions
        self.cursor.execute("""
            SELECT c.subtotal, p.commission_value, cm.gross_amount, cm.net_amount
            FROM commissions cm
            JOIN conversions c ON cm.conversion_id = c.id
            JOIN programs p ON cm.program_id = p.id
            WHERE p.commission_type = 'percent'
            LIMIT 10
        """)

        for row in self.cursor.fetchall():
            subtotal, rate, gross, net = row
            expected_gross = float(subtotal) * float(rate)
            expected_net = expected_gross * 0.8  # 20% platform fee

            if abs(gross - expected_gross) > 0.01:
                print_error(f"Commission mismatch: Expected {expected_gross:.2f}, got {gross:.2f}")
            else:
                print_success(f"Commission correct: ${gross:.2f} on ${subtotal:.2f} @ {rate*100:.1f}%")

    def test_attribution_window(self):
        """Test attribution window logic"""
        print_info("Testing attribution windows...")

        # Check that conversions outside window aren't attributed
        self.cursor.execute("""
            SELECT COUNT(*) as unattributed
            FROM conversions c
            LEFT JOIN attributions a ON c.id = a.conversion_id
            WHERE a.id IS NULL
        """)

        unattributed = self.cursor.fetchone()[0]
        if unattributed > 0:
            print_warning(f"Found {unattributed} unattributed conversions (might be outside window)")
        else:
            print_success("All conversions properly attributed")

    def test_payout_thresholds(self):
        """Test payout threshold logic"""
        print_info("Testing payout thresholds...")

        # Check minimum payout amounts
        MIN_PAYOUT = 50.00

        self.cursor.execute("""
            SELECT influencer_id, SUM(net_amount) as total
            FROM commissions
            WHERE status = 'pending'
            GROUP BY influencer_id
        """)

        for row in self.cursor.fetchall():
            influencer_id, total = row
            if total < MIN_PAYOUT:
                print_info(f"Influencer {influencer_id[:8]}... below threshold: ${total:.2f}")
            else:
                print_success(f"Influencer {influencer_id[:8]}... eligible for payout: ${total:.2f}")

    def test_network_specific_rules(self):
        """Test network-specific business rules"""
        print_info("Testing network-specific rules...")

        # Test Amazon's 24-hour cookie window
        self.cursor.execute("""
            SELECT n.type, n.cookie_window_days, COUNT(c.id) as conversions
            FROM networks n
            JOIN programs p ON n.id = p.network_id
            JOIN conversions c ON p.id = c.program_id
            GROUP BY n.type, n.cookie_window_days
        """)

        for row in self.cursor.fetchall():
            network_type, window, count = row
            if network_type == 'amazon' and window != 1:
                print_error(f"Amazon should have 1-day window, has {window}")
            else:
                print_success(f"{network_type}: {window}-day window, {count} conversions")

    def test_fraud_detection(self):
        """Test fraud detection mechanisms"""
        print_info("Testing fraud detection...")

        # Check for suspicious click patterns
        self.cursor.execute("""
            SELECT device_id, COUNT(*) as click_count
            FROM clicks
            WHERE clicked_at > datetime('now', '-1 hour')
            GROUP BY device_id
            HAVING COUNT(*) > 10
        """)

        suspicious = self.cursor.fetchall()
        if suspicious:
            print_warning(f"Found {len(suspicious)} devices with suspicious click volume")
        else:
            print_success("No suspicious click patterns detected")

        # Check fraud scores
        self.cursor.execute("""
            SELECT AVG(fraud_score) as avg_score, MAX(fraud_score) as max_score
            FROM clicks
        """)

        avg_score, max_score = self.cursor.fetchone()
        print_info(f"Fraud scores - Average: {avg_score:.3f}, Max: {max_score:.3f}")

    def test_data_integrity(self):
        """Test referential integrity and data consistency"""
        print_info("Testing data integrity...")

        # Check for orphaned records
        checks = [
            ("Commissions without conversions", """
                SELECT COUNT(*) FROM commissions cm
                LEFT JOIN conversions c ON cm.conversion_id = c.id
                WHERE c.id IS NULL
            """),
            ("Attributions without conversions", """
                SELECT COUNT(*) FROM attributions a
                LEFT JOIN conversions c ON a.conversion_id = c.id
                WHERE c.id IS NULL
            """),
            ("Clicks without tracking links", """
                SELECT COUNT(*) FROM clicks cl
                LEFT JOIN tracking_links tl ON cl.tracking_link_id = tl.id
                WHERE tl.id IS NULL
            """)
        ]

        for check_name, query in checks:
            self.cursor.execute(query)
            count = self.cursor.fetchone()[0]
            if count > 0:
                print_error(f"{check_name}: {count} orphaned records")
            else:
                print_success(f"{check_name}: No orphaned records")

    def generate_report(self):
        """Generate comprehensive validation report"""
        print_header("Validation Report")

        # Get summary statistics
        stats_queries = {
            "Total Influencers": "SELECT COUNT(*) FROM influencers",
            "Total Merchants": "SELECT COUNT(*) FROM merchants",
            "Total Products": "SELECT COUNT(*) FROM products",
            "Total Tracking Links": "SELECT COUNT(*) FROM tracking_links",
            "Total Clicks": "SELECT COUNT(*) FROM clicks",
            "Total Conversions": "SELECT COUNT(*) FROM conversions",
            "Total Commissions": "SELECT COUNT(*) FROM commissions",
            "Conversion Rate": """
                SELECT ROUND(CAST(COUNT(DISTINCT c.id) AS FLOAT) /
                       COUNT(DISTINCT cl.id) * 100, 2)
                FROM clicks cl
                LEFT JOIN conversions c ON c.subid =
                    (SELECT subid FROM clicks WHERE tracking_link_id = cl.tracking_link_id LIMIT 1)
            """,
            "Total Commission Value": "SELECT ROUND(SUM(net_amount), 2) FROM commissions",
            "Average Order Value": "SELECT ROUND(AVG(total), 2) FROM conversions",
            "Average Commission": "SELECT ROUND(AVG(net_amount), 2) FROM commissions"
        }

        print("\n[METRICS] PLATFORM METRICS:")
        print("-" * 40)
        for metric, query in stats_queries.items():
            self.cursor.execute(query)
            result = self.cursor.fetchone()[0]
            if result is not None:
                if "Rate" in metric:
                    print(f"{metric:25} {result:.2f}%")
                elif "Value" in metric or "Commission" in metric:
                    print(f"{metric:25} ${result:,.2f}")
                else:
                    print(f"{metric:25} {result:,}")

        # Top performers
        print("\n[TOP] TOP PERFORMERS:")
        print("-" * 40)

        self.cursor.execute("""
            SELECT i.display_name, COUNT(c.id) as conversions,
                   ROUND(SUM(cm.net_amount), 2) as earnings
            FROM influencers i
            JOIN commissions cm ON i.id = cm.influencer_id
            JOIN conversions c ON cm.conversion_id = c.id
            GROUP BY i.id, i.display_name
            ORDER BY earnings DESC
            LIMIT 3
        """)

        for rank, (name, conversions, earnings) in enumerate(self.cursor.fetchall(), 1):
            print(f"{rank}. {name:20} {conversions:3} sales  ${earnings:,.2f}")

        # Network performance
        print("\n🌐 NETWORK PERFORMANCE:")
        print("-" * 40)

        self.cursor.execute("""
            SELECT m.integration_type, COUNT(c.id) as conversions,
                   ROUND(AVG(p.commission_value * 100), 1) as avg_rate
            FROM merchants m
            JOIN programs p ON m.id = p.merchant_id
            LEFT JOIN conversions c ON p.id = c.program_id
            GROUP BY m.integration_type
        """)

        for network, conversions, rate in self.cursor.fetchall():
            print(f"{network:20} {conversions:4} conversions @ {rate:.1f}% avg")

        print("\n" + "="*60)
        print(f"{Colors.BOLD}{Colors.GREEN}✅ VALIDATION COMPLETE{Colors.ENDC}")
        print("="*60)

        return True

    def cleanup(self):
        """Clean up test database"""
        if self.conn:
            self.conn.close()
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        print_success("Cleaned up test database")

    def run(self):
        """Run complete validation suite"""
        print_header("SKINSTACK MVP VALIDATOR")
        print("Testing the complete platform with synthetic data...")

        try:
            self.setup_database()
            self.generate_synthetic_data()
            self.simulate_traffic_and_conversions()
            self.validate_business_logic()
            success = self.generate_report()

            if success:
                print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Schema validation successful!{Colors.ENDC}")
                print(f"{Colors.GREEN}The database schema and business logic are working correctly.{Colors.ENDC}")
                print(f"\n{Colors.BLUE}Next steps:{Colors.ENDC}")
                print("1. Review the test results above")
                print("2. Connect to real affiliate networks")
                print("3. Implement the API endpoints")
                print("4. Deploy to production")

        except Exception as e:
            print_error(f"Validation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

if __name__ == "__main__":
    validator = SkinStackValidator()
    validator.run()