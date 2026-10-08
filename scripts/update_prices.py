import re
from pathlib import Path

# Mapping from menu item -> desired price (include ₦ and commas)
PRICES = {
    "Sweet Corn Soup": "₦2,500",
    "Cream of Chicken Soup": "₦2,500",
    "English Breakfast": "₦11,000",
    "American Breakfast": "₦8,000",
    "Nigerian Styled Breakfast": "₦8,000",
    "White Rice & Stew": "₦5,000",
    "White Basmati Rice & Stew": "₦6,000",
    "White Spaghetti & Stew": "₦5,500",
    "Yam & Egg Sauce": "₦6,000",
    "Plantain & Egg Sauce": "₦6,000",
    "Jollof Rice": "₦5,000",
    "White Rice": "₦3,000",
    "Braised Rice": "₦3,000",
    "Rice & Beans": "₦10,000",
    "Vegetable Fried Rice": "₦6,000",
    "Coconut Rice": "₦6,000",
    "Beef Rice": "₦7,000",
    "Native Rice": "₦7,000",
    "BBQ Chicken Wings": "₦7,000",
    "Chicken Drumlets": "₦7,000",
    "Fish Fingers": "₦5,500",
    "Butterfly Prawn": "₦9,000",
    "Spring Roll": "₦5,000",
    "Samosa": "₦5,000",
    "Spicy Chicken Kebab": "₦7,000",
    "Peppered Chicken": "₦8,000",
    "Chicken & Chips": "₦11,000",
    "Mixmeat Fried Rice (Basmati)": "₦8,000",
    "Mix Meat Fried Rice": "₦8,000",
    "Beef Rice (Basmati)": "₦7,000",
    "Special Fried Rice": "₦9,000",
    "Gabby’s Special Rice": "₦10,000",
    "Pineapple Fried Rice": "₦8,000",
    "Spanish Fried Rice": "₦9,000",
    "White Basmati Rice": "₦4,000",
    "White Spaghetti": "₦6,000",
    "Jollof Spaghetti": "₦6,000",
    "Fried Plantain": "₦2,000",
    "Chips (Yam)": "₦3,000",
    "Shredded Beef Sauce": "₦7,000",
    "Mashed Potatoes": "₦5,000",
    "Sautéed Potatoes": "₦3,000",
    "Chips (Potatoes)": "₦3,000",
    "Chicken": "₦8,000",
    "Turkey": "₦8,000",
    "Chicken Wings": "₦5,500",
    "Turkey Gizzard": "₦8,000",
    "Goat Meat": "₦8,000",
    "Cow Tail": "₦7,000",
    "Cow Head": "₦6,500",
    "Beef": "₦6,000",
    "Cow Leg": "₦8,000",
    "Tilapia": "₦6,000",
    "Croaker Fish": "₦7,000",
    "Catfish": "₦5,000",
    "Red Snapper Fish": "₦12,000",
    "Chinese Fish": "₦12,000",
    "Prawn": "₦12,000",
    "Snail": "₦9,500",
    "Dry Fish": "₦6,000",
    "Bush Meat": "₦5,000",
    "Pork Meat": "₦5,000",
    "Peppered Pork": "₦5,000",
    "Assorted Meat": "₦5,000",
    "Porridge Yam": "₦6,000",
    "Porridge Potatoes": "₦6,000",
    "Mix Porridge": "₦8,000",
    "Porridge Plantain": "₦6,000",
    "Porridge Beans": "₦6,000",
    "White Rice with Palm Oil Sauce": "₦6,000",
    "Native Rice with Dried Fish Sauce": "₦11,000",
    "White Rice with Vegetable Sauce": "₦6,000",
    "Egusi Soup": "₦6,000",
    "Ogbono Soup": "₦6,000",
    "Vegetable Soup": "₦6,000",
    "Ukazi (Afang) Soup": "₦6,000",
    "Okra Soup": "₦6,000",
    "Oha Soup": "₦6,000",
    "Rivers Fisherman Soup": "₦25,000",
    "Efik Fisherman Soup": "₦8,000",
    "Seafood Okra": "₦9,000",
    "White Soup": "₦7,000",
    "Banga Soup": "₦6,000",
    "Bitter Leaf Soup": "₦6,000",
    "Garri": "₦1,000",
    "Semo": "₦1,500",
    "Wheat": "₦1,000",
    "Oatmeal": "₦1,500",
    "Poundo": "₦1,500",
    "Plantain Swallow": "₦1,500",
    "Fufu": "₦1,000",
    "BBQ Catfish": "₦15,000",
    "BBQ Croaker Fish": "₦15,000",
    "BBQ Tilapia (Medium)": "₦13,000",
    "BBQ Tilapia (Big)": "₦15,000",
    "Coleslaw Salad": "₦2,500",
    "Fruits Salad": "₦5,000",
    "Chicken Salad": "₦9,000",
    "Avocado & Prawn Salad": "₦10,000",
    "Prawn Cocktail Salad": "₦8,000",
    "Caesar Salad": "₦7,000",
    "Potato Chips": "₦3,000",
    "Matching Ground / Piompiom": "₦5,000",
    "Isi Ewu": "₦12,000",
    "Nkwobi": "₦7,000",
    "Nkwobi & Piompiom": "₦8,000",
    "Grilled Tilapia (Full) & Pressed Plantain": "₦13,000",
    "Akidi & Achicha": "₦8,000",
    "Abacha & Ugba": "₦7,000",
    "Ukwa": "₦8,000",
    "Amala & Ewedu/Gbegiri": "₦8,000",
    "Seafood Pasta": "₦13,000",
    "Alfredo Pasta": "₦8,000",
    "Spaghetti Bolognaise": "₦8,000",
    "Spaghetti & Meatballs": "₦10,000",
    "Singapore Noodles": "₦8,000",
    "Seafood Creamy Pasta": "₦13,000",
    "Noodles & Egg & Sausages": "₦6,000",
    "Jollof Spaghetti": "₦5,000",
    "Grilled Jumbo Prawn": "₦12,000",
    "Curried Prawn in Coconut Milk": "₦13,000",
    "Prawn in Tomatoes Garlic Sauce": "₦13,000",
    "Prawn in Sweet & Sour Sauce": "₦13,000",
    "Mixed Seafood in Cream Sauce": "₦15,000",
    "Fish Fillet in Lemon Sauce": "₦8,000",
    "Grilled Fish Curry": "₦8,000",
    "Grilled Tilapia (Full) & Pressed Plantain": "₦15,000",
    "Fish & Vegetable Stir Fry": "₦8,000",
    "Peppered Fresh Fish (Red Snapper/Shine Nose)": "₦10,000",
    "Peppered Croaker Fish": "₦7,000",
    "Peppered Tilapia Fish": "₦6,000",
    "Peppered Catfish": "₦5,500",
    "Chicken Shawarma": "₦4,500",
    "Beef Shawarma": "₦4,500",
    "Grilled Pork Shawarma": "₦5,000",
    "Asun (Goat) Shawarma": "₦5,000",
    "Bush Meat Shawarma": "₦5,500",
    "Mix Shawarma": "₦6,500",
    "China Pot with Rice": "₦15,000",
    "China Pot with Pasta": "₦15,000",
    "Full Catfish Pepper Soup": "₦15,000",
    "Red Snapper Head": "₦12,000",
    "Full Tilapia Fish Pepper Soup": "₦14,000",
    "Seafood Platter": "₦60,000",
    "Native Platter": "₦70,000",
    "Vegetable Platter": "₦30,000",
    "Seafood Boil": "₦25,000",
    "Chef’s Special Platter": "₦100,000",
    # Drinks
    "Big Gordon": "₦12,000",
    "Small Gordon": "₦5,000",
    "Bombay Sapphire": "₦35,000",
    "Sierra": "₦50,000",
    "Tequila Short": "₦4,000",
    "Olmeca Tequila": "₦45,000",
    "Chivita": "₦3,500",
    "Active": "₦3,500",
    "Exotic": "₦3,500",
    "Hollandia": "₦3,500",
    "Tomi Cranberry": "₦3,500",
    "Black Bullet": "₦3,000",
    "Fearless": "₦1,500",
    "Monster": "₦2,500",
    "Predator": "₦1,500",
    "Red Bull": "₦2,500",
    "Hennessy": "₦100,000",
    "Martell Swift Blue": "₦140,000",
    "Hennessy VSOP": "₦180,000",
    "Martel VS": "₦100,000",
    "Jack Daniel": "₦40,000",
    "Jameson Black": "₦70,000",
    "Black Label": "₦60,000",
    "Monkey Shoulder": "₦70,000",
    "Teeling Small Batch": "₦70,000",
    "William Lawson": "₦25,000",
    "Jameson Green": "₦35,000",
    "Teeling Gram": "₦80,000",
    "Four Cousin": "₦20,000",
    "Carlo Rossi": "₦20,000",
    "Martineli's": "₦20,000",
    "4th Street": "₦12,000",
    "Silk & Spice": "₦30,000",
    "Thomas Barton": "₦40,000",
    "Escardo Rojo": "₦35,000",
    "Agor": "₦20,000",
    "Chamdor": "₦12,000",
    "Sweet Kiss": "₦20,000",
    "Toma-Toma": "₦12,000",
    "Castillo Red Wine": "₦15,000",
    "Drostdy Hof Red Wine": "₦15,000",
    "Andre": "₦35,000",
    "Coke": "₦1,500",
    "Sprite": "₦1,500",
    "Water": "₦700",
    "Fanta": "₦1,500",
    "Big Heineken": "₦3,000",
    "Small Heineken": "₦2,000",
    "Budweiser": "₦3,000",
    "Smirnoff Double Black": "₦2,500",
    "Star Radler": "₦2,000",
    "Desperado": "₦2,000",
    "Flying Fish": "₦2,500",
    "Hero": "₦2,500",
    "Life": "₦2,000",
    "Medium Stout": "₦2,000",
    "Tiger": "₦2,500",
    "Maltina": "₦1,500",
    "Schweppes": "₦1,500",
    "Big Smirnoff Ice": "₦3,000",
    "Legend": "₦2,500",
    "Small Smirnoff White": "₦2,000",
    "Castle Lite": "₦2,500",
    "Tonic": "₦2,000",
    "Gulder": "₦2,000",
    "Balarie": "₦90,000",
    "Absolut Vodka": "₦35,000",
    "Smirnoff Vodka (Big)": "₦20,000",
    "Smirnoff Vodka (Small)": "₦5,000",
    "Buen Amigo": "₦35,000",
    "Buen Amigo Gold": "₦40,000",
}


def find_price_line(lines, start_idx):
    # search current line and next 4 lines for a line containing a price pattern
    price_re = re.compile(r'₦\s*[\d,]+')
    for i in range(start_idx, min(len(lines), start_idx + 5)):
        if price_re.search(lines[i]):
            return i
    return None


def replace_price_in_line(line, new_price):
    price_re = re.compile(r'₦\s*[\d,]+')
    if price_re.search(line):
        return price_re.sub(new_price, line)
    # fallback: attempt to place price before closing </p>
    if '</p>' in line:
        return line.replace('</p>', f'{new_price}</p>')
    return line


def normalize(s):
    return re.sub(r'\s+', ' ', s).strip().lower()


def main():
    root = Path('.').resolve()
    html_files = list(root.glob('*.html'))
    changed_files = []
    updated_items = set()
    not_found = set(PRICES.keys())

    for fp in html_files:
        text = fp.read_text(encoding='utf-8')
        lines = text.splitlines()
        original = lines.copy()
        modified = False

        for item, new_price in PRICES.items():
            pattern = re.compile(re.escape(item), re.IGNORECASE)
            for idx, line in enumerate(lines):
                if pattern.search(line):
                    # find the line that likely contains the price
                    price_line_idx = find_price_line(lines, idx)
                    if price_line_idx is not None:
                        old = lines[price_line_idx]
                        new = replace_price_in_line(old, new_price)
                        if new != old:
                            lines[price_line_idx] = new
                            modified = True
                            updated_items.add(item)
                            not_found.discard(item)
                    else:
                        # attempt to insert a price tag on the same line if the item and price are on same element
                        if '<p' in line and '</p>' in line:
                            new_line = replace_price_in_line(line, new_price)
                            if new_line != line:
                                lines[idx] = new_line
                                modified = True
                                updated_items.add(item)
                                not_found.discard(item)

        if modified:
            fp.write_text('\n'.join(lines), encoding='utf-8')
            changed_files.append(str(fp))

    # Report
    print('Updated files:')
    for f in changed_files:
        print(' -', f)
    print('\nUpdated items count:', len(updated_items))
    if not_found:
        print('\nItems not found in any HTML file:')
        for it in sorted(not_found):
            print(' -', it)


if __name__ == '__main__':
    main()
