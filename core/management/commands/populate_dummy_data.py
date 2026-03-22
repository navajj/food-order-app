from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Customer, Restaurant, MenuItem, Order, OrderItem
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate database with dummy data for testing'

    def handle(self, *args, **options):
        # Clear existing data
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        MenuItem.objects.all().delete()
        Restaurant.objects.all().delete()
        Customer.objects.all().delete()
        User.objects.filter(username__startswith='customer_').delete()

        self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        # Create dummy users and customers
        customers_data = [
            {'username': 'customer_john', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'customer_jane', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'customer_bob', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Johnson'},
            {'username': 'customer_alice', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Williams'},
        ]

        customers = []
        for data in customers_data:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password='testpass123'
            )
            customer = Customer.objects.create(
                user=user,
                phone='+1-555-0100',
                address='123 Main St, Anytown, USA'
            )
            customers.append(customer)

        self.stdout.write(self.style.SUCCESS(f'Created {len(customers)} customers'))

        # Create dummy restaurants
        restaurants_data = [
            {
                'name': 'The Pizza Place',
                'description': 'Classic Italian pizzas and pasta dishes'
            },
            {
                'name': 'Sushi Master',
                'description': 'Fresh sushi and Japanese cuisine'
            },
            {
                'name': 'Burger King',
                'description': 'Delicious burgers and fries'
            },
            {
                'name': 'Thai Taste',
                'description': 'Authentic Thai food and curries'
            },
        ]

        restaurants = []
        for data in restaurants_data:
            restaurant = Restaurant.objects.create(
                name=data['name'],
                description=data['description'],
                is_active=True
            )
            restaurants.append(restaurant)

        self.stdout.write(self.style.SUCCESS(f'Created {len(restaurants)} restaurants'))

        # Create menu items for each restaurant
        menu_items_data = {
            0: [  # Pizza Place
                {'name': 'Margherita Pizza', 'description': 'Fresh mozzarella, basil, tomato', 'price': '12.99', 'category': 'Pizza'},
                {'name': 'Pepperoni Pizza', 'description': 'Classic pepperoni pizza', 'price': '13.99', 'category': 'Pizza'},
                {'name': 'Spaghetti Carbonara', 'description': 'Creamy pasta with bacon', 'price': '11.99', 'category': 'Pasta'},
                {'name': 'Caesar Salad', 'description': 'Fresh greens with parmesan', 'price': '8.99', 'category': 'Salad'},
            ],
            1: [  # Sushi Master
                {'name': 'California Roll', 'description': 'Crab, avocado, cucumber', 'price': '9.99', 'category': 'Rolls'},
                {'name': 'Spicy Tuna Roll', 'description': 'Spicy tuna with avocado', 'price': '10.99', 'category': 'Rolls'},
                {'name': 'Sashimi Platter', 'description': 'Assorted fresh sashimi', 'price': '24.99', 'category': 'Sashimi'},
                {'name': 'Miso Soup', 'description': 'Traditional miso soup', 'price': '3.99', 'category': 'Soup'},
            ],
            2: [  # Burger King
                {'name': 'Classic Burger', 'description': 'Beef patty with all the fixings', 'price': '8.99', 'category': 'Burgers'},
                {'name': 'Double Cheeseburger', 'description': 'Two patties and two slices of cheese', 'price': '10.99', 'category': 'Burgers'},
                {'name': 'French Fries', 'description': 'Golden crispy fries', 'price': '3.99', 'category': 'Sides'},
                {'name': 'Onion Rings', 'description': 'Crispy onion rings', 'price': '4.49', 'category': 'Sides'},
            ],
            3: [  # Thai Taste
                {'name': 'Pad Thai', 'description': 'Stir-fried rice noodles with shrimp', 'price': '11.99', 'category': 'Noodles'},
                {'name': 'Green Curry', 'description': 'Spicy green curry with chicken', 'price': '12.99', 'category': 'Curry'},
                {'name': 'Tom Yum Soup', 'description': 'Spicy and sour soup with shrimp', 'price': '8.99', 'category': 'Soup'},
                {'name': 'Spring Rolls', 'description': 'Fresh spring rolls (4 pieces)', 'price': '6.99', 'category': 'Appetizers'},
            ],
        }

        menu_items = []
        for restaurant_idx, items in menu_items_data.items():
            for item_data in items:
                menu_item = MenuItem.objects.create(
                    restaurant=restaurants[restaurant_idx],
                    name=item_data['name'],
                    description=item_data['description'],
                    price=Decimal(item_data['price']),
                    category=item_data['category'],
                    is_available=True
                )
                menu_items.append(menu_item)

        self.stdout.write(self.style.SUCCESS(f'Created {len(menu_items)} menu items'))

        # Create dummy orders
        orders = []
        now = timezone.now()

        # Order 1: John from Pizza Place
        order1 = Order.objects.create(
            customer=customers[0],
            restaurant=restaurants[0],
            status=Order.Status.DELIVERED,
            notes='Extra cheese please',
            created_at=now - timedelta(days=3)
        )
        OrderItem.objects.create(
            order=order1,
            menu_item=menu_items[0],  # Margherita Pizza
            quantity=2,
            unit_price=Decimal('12.99')
        )
        OrderItem.objects.create(
            order=order1,
            menu_item=menu_items[3],  # Caesar Salad
            quantity=1,
            unit_price=Decimal('8.99')
        )
        order1.total = Decimal('34.97')
        order1.save()
        orders.append(order1)

        # Order 2: Jane from Sushi Master
        order2 = Order.objects.create(
            customer=customers[1],
            restaurant=restaurants[1],
            status=Order.Status.READY,
            notes='No wasabi',
            created_at=now - timedelta(days=1)
        )
        OrderItem.objects.create(
            order=order2,
            menu_item=menu_items[4],  # California Roll
            quantity=2,
            unit_price=Decimal('9.99')
        )
        OrderItem.objects.create(
            order=order2,
            menu_item=menu_items[7],  # Miso Soup
            quantity=2,
            unit_price=Decimal('3.99')
        )
        order2.total = Decimal('27.96')
        order2.save()
        orders.append(order2)

        # Order 3: Bob from Burger King
        order3 = Order.objects.create(
            customer=customers[2],
            restaurant=restaurants[2],
            status=Order.Status.PREPARING,
            notes='',
            created_at=now - timedelta(hours=2)
        )
        OrderItem.objects.create(
            order=order3,
            menu_item=menu_items[9],  # Classic Burger
            quantity=1,
            unit_price=Decimal('8.99')
        )
        OrderItem.objects.create(
            order=order3,
            menu_item=menu_items[11],  # Onion Rings
            quantity=1,
            unit_price=Decimal('4.49')
        )
        order3.total = Decimal('13.48')
        order3.save()
        orders.append(order3)

        # Order 4: Alice from Thai Taste
        order4 = Order.objects.create(
            customer=customers[3],
            restaurant=restaurants[3],
            status=Order.Status.PENDING,
            notes='Mild spice level',
            created_at=now - timedelta(minutes=30)
        )
        OrderItem.objects.create(
            order=order4,
            menu_item=menu_items[12],  # Pad Thai
            quantity=1,
            unit_price=Decimal('11.99')
        )
        OrderItem.objects.create(
            order=order4,
            menu_item=menu_items[14],  # Tom Yum Soup
            quantity=1,
            unit_price=Decimal('8.99')
        )
        order4.total = Decimal('20.98')
        order4.save()
        orders.append(order4)

        self.stdout.write(self.style.SUCCESS(f'Created {len(orders)} orders'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Database populated successfully!\n'
                f'  - {len(customers)} customers\n'
                f'  - {len(restaurants)} restaurants\n'
                f'  - {len(menu_items)} menu items\n'
                f'  - {len(orders)} orders'
            )
        )
