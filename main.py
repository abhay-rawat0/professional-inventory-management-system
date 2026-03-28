import json
import os
from datetime import datetime
import csv


# ============================================
# PRODUCT CLASS
# ============================================

class Product:
    """Represents a product in the inventory"""

    def __init__(self, name, price, stock, category, product_id=None):
        self.product_id = product_id or self.generate_id()
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated = self.created_date

    @staticmethod
    def generate_id():
        """Generate a unique product ID"""
        return f"PROD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"

    def display(self):
        """Display product details"""
        print(f"\n  ID: {self.product_id}")
        print(f"  Name: {self.name}")
        print(f"  Price: ${self.price:.2f}")
        print(f"  Stock: {self.stock}")
        print(f"  Category: {self.category}")
        print(f"  Added: {self.created_date}")
        print(f"  Last Updated: {self.last_updated}")

    def to_dict(self):
        """Convert product to dictionary for JSON storage"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "created_date": self.created_date,
            "last_updated": self.last_updated
        }

    def update_stock(self, quantity):
        """Update stock quantity and timestamp"""
        self.stock += quantity
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================
# INVENTORY MANAGER CLASS
# ============================================

class InventoryManager:
    """Manages all inventory operations"""

    def __init__(self):
        self.products = []
        self.sales_history = []
        self.revenue = 0
        self.filename = "inventory.json"
        self.sales_filename = "sales.json"
        self.load_inventory()
        self.load_sales_history()

    # ============================================
    # CORE CRUD OPERATIONS
    # ============================================

    def add_product(self):
        """Add a new product to inventory"""
        print("\n" + "=" * 50)
        print("ADD NEW PRODUCT")
        print("=" * 50)

        # Get product details with validation
        name = self.get_valid_input("Product name: ", str, is_required=True)

        # Check for duplicate product name
        if self.find_product_by_name(name):
            print(f"\n❌ Product '{name}' already exists!")
            return

        price = self.get_valid_input("Price: $", float, min_value=0, is_required=True)
        stock = self.get_valid_input("Stock quantity: ", int, min_value=0, is_required=True)
        category = self.get_valid_input("Category: ", str, is_required=True, default="General")

        # Create and add product
        product = Product(name, price, stock, category)
        self.products.append(product)
        self.save_inventory()

        print(f"\n✅ Product '{name}' added successfully!")
        print(f"   Product ID: {product.product_id}")

    def view_products(self):
        """Display all products with summary"""
        if not self.products:
            print("\n📦 No products in inventory.")
            return

        print("\n" + "=" * 70)
        print("INVENTORY LIST")
        print("=" * 70)

        # Show summary statistics
        total_value = sum(p.price * p.stock for p in self.products)
        total_items = sum(p.stock for p in self.products)
        print(f"Total Products: {len(self.products)} | Total Items: {total_items} | Total Value: ${total_value:.2f}")
        print("-" * 70)

        # Display each product
        for i, product in enumerate(self.products, 1):
            print(f"\n[{i}] ", end="")
            product.display()
            print("  " + "-" * 50)

    def update_product(self):
        """Update existing product information"""
        if not self.products:
            print("\n📦 No products to update.")
            return

        self.view_products()

        try:
            choice = int(input("\nSelect product number to update: ")) - 1

            if 0 <= choice < len(self.products):
                product = self.products[choice]
                print(f"\n--- Updating: {product.name} ---")

                # Update name
                new_name = input(f"Current name: {product.name}\nNew name (Enter to skip): ")
                if new_name:
                    product.name = new_name

                # Update price
                new_price = input(f"Current price: ${product.price:.2f}\nNew price (Enter to skip): ")
                if new_price:
                    try:
                        product.price = float(new_price)
                    except ValueError:
                        print("Invalid price! Keeping original.")

                # Update stock
                new_stock = input(f"Current stock: {product.stock}\nNew stock (Enter to skip): ")
                if new_stock:
                    try:
                        product.stock = int(new_stock)
                    except ValueError:
                        print("Invalid stock! Keeping original.")

                # Update category
                new_category = input(f"Current category: {product.category}\nNew category (Enter to skip): ")
                if new_category:
                    product.category = new_category

                # Update timestamp
                product.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_inventory()

                print(f"\n✅ Product updated successfully!")
            else:
                print("\n❌ Invalid product number!")
        except ValueError:
            print("\n❌ Invalid input!")

    def delete_product(self):
        """Delete a product from inventory"""
        if not self.products:
            print("\n📦 No products to delete.")
            return

        self.view_products()

        try:
            choice = int(input("\nSelect product number to delete: ")) - 1

            if 0 <= choice < len(self.products):
                product = self.products[choice]
                confirm = input(f"\n⚠️  Are you sure you want to delete '{product.name}'? (y/n): ")

                if confirm.lower() == 'y':
                    self.products.pop(choice)
                    self.save_inventory()
                    print(f"\n✅ Product '{product.name}' deleted successfully!")
                else:
                    print("\n❌ Deletion cancelled.")
            else:
                print("\n❌ Invalid product number!")
        except ValueError:
            print("\n❌ Invalid input!")

    # ============================================
    # SEARCH AND FILTER
    # ============================================

    def search_products(self):
        """Search products by various criteria"""
        if not self.products:
            print("\n📦 No products to search.")
            return

        print("\n" + "=" * 50)
        print("SEARCH PRODUCTS")
        print("=" * 50)
        print("1. Search by name")
        print("2. Search by category")
        print("3. Search by price range")
        print("4. Search by stock level")

        choice = input("\nEnter choice (1-4): ")

        if choice == "1":
            term = input("Enter product name: ").lower()
            found = [p for p in self.products if term in p.name.lower()]

        elif choice == "2":
            term = input("Enter category: ").lower()
            found = [p for p in self.products if term in p.category.lower()]

        elif choice == "3":
            try:
                min_price = float(input("Minimum price: "))
                max_price = float(input("Maximum price: "))
                found = [p for p in self.products if min_price <= p.price <= max_price]
            except ValueError:
                print("\n❌ Invalid price values!")
                return

        elif choice == "4":
            try:
                max_stock = int(input("Maximum stock level: "))
                found = [p for p in self.products if p.stock <= max_stock]
            except ValueError:
                print("\n❌ Invalid stock value!")
                return
        else:
            print("\n❌ Invalid choice!")
            return

        if found:
            print(f"\n✅ Found {len(found)} product(s):")
            for product in found:
                product.display()
        else:
            print("\n❌ No products found!")

    def sort_products(self):
        """Sort products by different criteria"""
        if not self.products:
            print("\n📦 No products to sort.")
            return

        print("\n" + "=" * 50)
        print("SORT PRODUCTS")
        print("=" * 50)
        print("1. By name (A-Z)")
        print("2. By price (Low to High)")
        print("3. By price (High to Low)")
        print("4. By stock (Low to High)")
        print("5. By stock (High to Low)")

        choice = input("\nEnter choice (1-5): ")

        if choice == "1":
            self.products.sort(key=lambda x: x.name)
            print("\n✅ Sorted by name (A-Z)")
        elif choice == "2":
            self.products.sort(key=lambda x: x.price)
            print("\n✅ Sorted by price (Low to High)")
        elif choice == "3":
            self.products.sort(key=lambda x: x.price, reverse=True)
            print("\n✅ Sorted by price (High to Low)")
        elif choice == "4":
            self.products.sort(key=lambda x: x.stock)
            print("\n✅ Sorted by stock (Low to High)")
        elif choice == "5":
            self.products.sort(key=lambda x: x.stock, reverse=True)
            print("\n✅ Sorted by stock (High to Low)")
        else:
            print("\n❌ Invalid choice!")
            return

        self.view_products()

    # ============================================
    # SALES OPERATIONS
    # ============================================

    def sell_product(self):
        """Process a sale transaction"""
        if not self.products:
            print("\n📦 No products available for sale.")
            return

        self.view_products()

        try:
            choice = int(input("\nSelect product to sell: ")) - 1

            if 0 <= choice < len(self.products):
                product = self.products[choice]

                print(f"\n--- Selling: {product.name} ---")
                print(f"Price: ${product.price:.2f}")
                print(f"Available stock: {product.stock}")

                quantity = self.get_valid_input(
                    "Quantity to sell: ",
                    int,
                    min_value=1,
                    max_value=product.stock,
                    is_required=True
                )

                if quantity:
                    # Calculate total
                    total_amount = product.price * quantity

                    # Update stock
                    product.stock -= quantity

                    # Record sale
                    sale = {
                        "product_id": product.product_id,
                        "product_name": product.name,
                        "quantity": quantity,
                        "price": product.price,
                        "total": total_amount,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.sales_history.append(sale)

                    # Update revenue
                    self.revenue += total_amount

                    # Remove product if out of stock
                    if product.stock == 0:
                        print(f"\n⚠️  Product '{product.name}' is now out of stock!")
                        self.products.pop(choice)

                    # Save changes
                    self.save_inventory()
                    self.save_sales_history()

                    print(f"\n💰 Sale completed successfully!")
                    print(f"   Sold: {quantity} x {product.name}")
                    print(f"   Total: ${total_amount:.2f}")
                    print(f"   Revenue to date: ${self.revenue:.2f}")
                else:
                    print("\n❌ Invalid quantity!")
            else:
                print("\n❌ Invalid product number!")
        except ValueError:
            print("\n❌ Invalid input!")

    def view_sales_history(self):
        """Display sales history"""
        if not self.sales_history:
            print("\n📊 No sales recorded yet.")
            return

        print("\n" + "=" * 70)
        print("SALES HISTORY")
        print("=" * 70)

        total_sales = sum(sale["total"] for sale in self.sales_history)
        print(f"Total Transactions: {len(self.sales_history)}")
        print(f"Total Revenue: ${total_sales:.2f}")
        print("-" * 70)

        # Show last 20 sales
        start = max(0, len(self.sales_history) - 20)
        for i, sale in enumerate(self.sales_history[start:], 1):
            print(f"\n[{i}] {sale['date']}")
            print(f"    Product: {sale['product_name']}")
            print(f"    Quantity: {sale['quantity']}")
            print(f"    Price: ${sale['price']:.2f}")
            print(f"    Total: ${sale['total']:.2f}")

    # ============================================
    # REPORTS AND ANALYTICS
    # ============================================

    def generate_report(self):
        """Generate comprehensive inventory report"""
        if not self.products and not self.sales_history:
            print("\n📦 No data available for report.")
            return

        print("\n" + "=" * 70)
        print("INVENTORY MANAGEMENT REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        if self.products:
            # Product statistics
            total_products = len(self.products)
            total_stock = sum(p.stock for p in self.products)
            total_value = sum(p.price * p.stock for p in self.products)
            avg_price = total_value / total_stock if total_stock > 0 else 0

            print(f"\n📊 INVENTORY OVERVIEW:")
            print(f"   Total Products: {total_products}")
            print(f"   Total Stock Units: {total_stock}")
            print(f"   Total Inventory Value: ${total_value:.2f}")
            print(f"   Average Price: ${avg_price:.2f}")

            # Category breakdown
            categories = {}
            for p in self.products:
                categories[p.category] = categories.get(p.category, 0) + 1

            print(f"\n📁 CATEGORY BREAKDOWN:")
            for cat, count in sorted(categories.items()):
                cat_products = [p for p in self.products if p.category == cat]
                cat_value = sum(p.price * p.stock for p in cat_products)
                print(f"   {cat}: {count} products (Value: ${cat_value:.2f})")

            # Stock alerts
            low_stock = [p for p in self.products if p.stock <= 5]
            if low_stock:
                print(f"\n⚠️  LOW STOCK ALERT (<=5 units):")
                for p in low_stock:
                    print(f"   • {p.name}: {p.stock} units left")

            # Top products
            top_value = sorted(self.products, key=lambda x: x.price * x.stock, reverse=True)[:5]
            if top_value:
                print(f"\n🏆 TOP 5 MOST VALUABLE PRODUCTS:")
                for i, p in enumerate(top_value, 1):
                    value = p.price * p.stock
                    print(f"   {i}. {p.name}: ${value:.2f} ({p.stock} units @ ${p.price:.2f})")

        # Sales statistics
        if self.sales_history:
            total_sales = len(self.sales_history)
            total_revenue = sum(sale["total"] for sale in self.sales_history)

            print(f"\n💰 SALES OVERVIEW:")
            print(f"   Total Transactions: {total_sales}")
            print(f"   Total Revenue: ${total_revenue:.2f}")

            # Best selling products
            product_sales = {}
            for sale in self.sales_history:
                name = sale["product_name"]
                product_sales[name] = product_sales.get(name, 0) + sale["quantity"]

            best_sellers = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]
            if best_sellers:
                print(f"\n🏆 TOP 5 BEST SELLING PRODUCTS:")
                for i, (name, qty) in enumerate(best_sellers, 1):
                    print(f"   {i}. {name}: {qty} units sold")

    def check_low_stock(self):
        """Check and display low stock products"""
        threshold = self.get_valid_input(
            "Enter stock threshold (press Enter for default 5): ",
            int,
            min_value=1,
            default=5
        )

        low_stock = [p for p in self.products if p.stock <= threshold]

        if low_stock:
            print(f"\n⚠️  PRODUCTS WITH STOCK <= {threshold}:")
            print("-" * 50)
            for product in low_stock:
                print(f"\n  {product.name}")
                print(f"  Stock: {product.stock} units")
                print(f"  Category: {product.category}")
                print(f"  Price: ${product.price:.2f}")
        else:
            print(f"\n✅ No products with stock <= {threshold}")

    def view_revenue(self):
        """Display total revenue"""
        print("\n" + "=" * 50)
        print("REVENUE SUMMARY")
        print("=" * 50)
        print(f"Total Revenue: ${self.revenue:.2f}")

        if self.sales_history:
            today = datetime.now().strftime("%Y-%m-%d")
            today_sales = [s for s in self.sales_history if s["date"].startswith(today)]
            today_revenue = sum(s["total"] for s in today_sales)
            print(f"Today's Revenue: ${today_revenue:.2f}")

    # ============================================
    # FILE OPERATIONS
    # ============================================

    def save_inventory(self):
        """Save inventory to JSON file"""
        try:
            data = [product.to_dict() for product in self.products]
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Error saving inventory: {e}")
            return False

    def load_inventory(self):
        """Load inventory from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)

                for item in data:
                    product = Product(
                        item["name"],
                        item["price"],
                        item["stock"],
                        item["category"],
                        item.get("product_id")
                    )
                    product.created_date = item.get("created_date", product.created_date)
                    product.last_updated = item.get("last_updated", product.last_updated)
                    self.products.append(product)

                if self.products:
                    print(f"✅ Loaded {len(self.products)} products from {self.filename}")
        except Exception as e:
            print(f"⚠️  Could not load inventory: {e}")

    def save_sales_history(self):
        """Save sales history to JSON file"""
        try:
            with open(self.sales_filename, 'w') as f:
                json.dump(self.sales_history, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Error saving sales history: {e}")
            return False

    def load_sales_history(self):
        """Load sales history from JSON file"""
        try:
            if os.path.exists(self.sales_filename):
                with open(self.sales_filename, 'r') as f:
                    self.sales_history = json.load(f)
                self.revenue = sum(sale["total"] for sale in self.sales_history)
                if self.sales_history:
                    print(f"✅ Loaded {len(self.sales_history)} sales records")
        except Exception as e:
            print(f"⚠️  Could not load sales history: {e}")

    def export_to_csv(self):
        """Export inventory to CSV file"""
        if not self.products:
            print("\n📦 No products to export.")
            return

        filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['product_id', 'name', 'price', 'stock', 'category', 'created_date', 'last_updated']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for product in self.products:
                    writer.writerow(product.to_dict())

            print(f"\n✅ Inventory exported to '{filename}'")
        except Exception as e:
            print(f"\n❌ Export failed: {e}")

    # ============================================
    # UTILITY FUNCTIONS
    # ============================================

    def get_valid_input(self, prompt, data_type, min_value=None, max_value=None,
                        is_required=False, default=None, skip_prompt=False):
        """Generic function to get validated user input"""
        while True:
            if not skip_prompt:
                user_input = input(prompt)
            else:
                user_input = None

            # Handle empty input
            if not user_input:
                if is_required:
                    print("❌ This field is required!")
                    continue
                if default is not None:
                    return default
                return None

            try:
                # Convert to desired type
                if data_type == int:
                    value = int(user_input)
                elif data_type == float:
                    value = float(user_input)
                else:
                    value = user_input

                # Validate range
                if min_value is not None and value < min_value:
                    print(f"❌ Value must be at least {min_value}!")
                    continue
                if max_value is not None and value > max_value:
                    print(f"❌ Value must be at most {max_value}!")
                    continue

                return value
            except ValueError:
                print(f"❌ Invalid input! Please enter a valid {data_type.__name__}.")

    def find_product_by_name(self, name):
        """Find product by name (case-insensitive)"""
        for product in self.products:
            if product.name.lower() == name.lower():
                return product
        return None

    def get_statistics(self):
        """Get inventory statistics"""
        if not self.products:
            return None

        total_items = sum(p.stock for p in self.products)
        total_value = sum(p.price * p.stock for p in self.products)
        categories = len(set(p.category for p in self.products))

        return {
            "total_products": len(self.products),
            "total_items": total_items,
            "total_value": total_value,
            "categories": categories,
            "avg_price": total_value / total_items if total_items > 0 else 0
        }


# ============================================
# MAIN PROGRAM
# ============================================

def main():
    """Main program entry point"""
    manager = InventoryManager()

    while True:
        print("\n" + "=" * 60)
        print("    PROFESSIONAL INVENTORY MANAGEMENT SYSTEM")
        print("=" * 60)
        print("\n📦 PRODUCT MANAGEMENT")
        print("   1. Add Product")
        print("   2. View All Products")
        print("   3. Update Product")
        print("   4. Delete Product")
        print("   5. Search Products")
        print("   6. Sort Products")
        print("\n💰 SALES & TRANSACTIONS")
        print("   7. Sell Product")
        print("   8. View Sales History")
        print("   9. View Revenue")
        print("\n📊 REPORTS & ANALYTICS")
        print("  10. Generate Report")
        print("  11. Check Low Stock")
        print("\n💾 DATA MANAGEMENT")
        print("  12. Export to CSV")
        print("  13. Save Data")
        print("  14. Exit")
        print("=" * 60)

        choice = input("Enter your choice (1-14): ")

        if choice == "1":
            manager.add_product()
        elif choice == "2":
            manager.view_products()
        elif choice == "3":
            manager.update_product()
        elif choice == "4":
            manager.delete_product()
        elif choice == "5":
            manager.search_products()
        elif choice == "6":
            manager.sort_products()
        elif choice == "7":
            manager.sell_product()
        elif choice == "8":
            manager.view_sales_history()
        elif choice == "9":
            manager.view_revenue()
        elif choice == "10":
            manager.generate_report()
        elif choice == "11":
            manager.check_low_stock()
        elif choice == "12":
            manager.export_to_csv()
        elif choice == "13":
            manager.save_inventory()
            manager.save_sales_history()
            print("\n✅ All data saved successfully!")
        elif choice == "14":
            # Save before exit
            manager.save_inventory()
            manager.save_sales_history()
            print("\n" + "=" * 60)
            print("👋 Thank you for using Inventory Management System!")
            print("   Goodbye!")
            print("=" * 60)
            break
        else:
            print("\n❌ Invalid choice! Please enter 1-14.")

        input("\nPress Enter to continue...")


# ============================================
# PROGRAM ENTRY POINT
# ============================================

if __name__ == "__main__":
    main()